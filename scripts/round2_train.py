# %% [markdown]
# # Round 2 Training Notebook — GEO Audit Environment
#
# **Goal**: show the environment is usable as a real training loop where
# agent behavior measurably improves against structured environment rewards.
#
# **Split at every `# %%` marker to run as Colab cells.**

# %% [markdown]
# ## Section A — Setup

# %%
# ── Install dependencies (run once) ──────────────────────────────────────────
# !pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
# !pip install trl transformers datasets accelerate bitsandbytes

# %%
# ── Clone repo (fill in your GitHub URL) ─────────────────────────────────────
# !git clone https://github.com/YOUR_USERNAME/rl-geo-auditor.git
# import os; os.chdir("rl-geo-auditor")

# ── Or if running locally, just make sure you are in the project root ─────────
import sys, os
sys.path.insert(0, os.path.abspath("."))

# %%
import json
import random
import re
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List

from server.environment import GeoAuditEnvironment
from server.grader import calculate_reward
from server.models import GeoAuditAction

random.seed(42)
np.random.seed(42)

# %%
# Verify environment loads and one task runs
env = GeoAuditEnvironment()
obs = env.reset(task_difficulty="easy")
print("Environment OK")
print(f"  URL:   {obs.page.url}")
print(f"  Query: {obs.page.target_query}")
print(f"  Steps: {obs.step_count}/{obs.max_steps}")

# %% [markdown]
# ## Section B — Baseline Run (Heuristic Policy)
#
# Run the existing heuristic policy on all pages to establish the anchor score.

# %%
from inference import plan_actions, normalize_submission_score

DIFFICULTIES = ["easy", "medium", "hard"]
SUCCESS_THRESHOLD = 0.5
EXPERIMENT_MODE = "all"


def run_heuristic_episode(difficulty: str) -> Dict:
    env = GeoAuditEnvironment()
    obs = env.reset(task_difficulty=difficulty)
    actions = plan_actions(obs)
    rewards = []
    for action in actions:
        obs = env.step(action)
        rewards.append(obs.reward)
        if obs.done:
            break
    score = normalize_submission_score(obs.reward)
    return {
        "difficulty": difficulty,
        "score": score,
        "flagged": [i["type"] for i in obs.flagged_issues],
        "rewards": rewards,
    }


def run_heuristic_baseline(n_per_difficulty: int = 10) -> List[Dict]:
    results = []
    for diff in DIFFICULTIES:
        for _ in range(n_per_difficulty):
            results.append(run_heuristic_episode(diff))
    return results


print("Running heuristic baseline (30 episodes) …")
heuristic_results = run_heuristic_baseline(n_per_difficulty=10)
heuristic_scores = [r["score"] for r in heuristic_results]
print(f"Heuristic baseline  avg={np.mean(heuristic_scores):.3f}  "
      f"min={np.min(heuristic_scores):.3f}  max={np.max(heuristic_scores):.3f}")

for diff in DIFFICULTIES:
    subset = [r["score"] for r in heuristic_results if r["difficulty"] == diff]
    print(f"  {diff:6s}: {np.mean(subset):.3f}")

# %%
# Example heuristic audit output
example = heuristic_results[0]
print(f"Example heuristic run ({example['difficulty']}):")
print(f"  score:   {example['score']:.3f}")
print(f"  flagged: {example['flagged']}")

# %% [markdown]
# ## Section C — Training Configuration

# %%
MODEL_NAME = "unsloth/Qwen2.5-7B-Instruct"
MAX_GENERATION_TOKENS = 80

ISSUE_TYPES = GeoAuditEnvironment.ISSUE_TYPES
POSITIVE_TYPES = GeoAuditEnvironment.POSITIVE_TYPES

# 5 issue types with clear signal in page data — covers easy + medium + hard
ACTIVE_ISSUE_TYPES = [
    "thin_content",           # word_count low
    "missing_meta_description",  # meta_description missing
    "no_direct_answer",       # first paragraph doesn't answer query
    "no_sources",             # has_sources=False, source_count=0
    "no_headers",             # headers list empty
]

SYSTEM_PROMPT = f"""You are a GEO audit expert. Given structured signals from a webpage, identify GEO issues.

Return ONLY a JSON object with this exact format:
{{"issues":[{{"type":"<issue_type>","severity":"<critical|high|medium|low>"}}]}}

Valid issue types: {', '.join(ACTIVE_ISSUE_TYPES)}

Signals to check:
- thin_content: word_count is very low (under 300)
- missing_meta_description: meta_description is missing or empty
- no_direct_answer: first paragraph does not answer the target query
- no_sources: has_sources is False and source_count is 0
- no_headers: headers list is empty or missing

Rules:
- Only flag issues clearly supported by the signals above.
- Do not invent issues. False positives are penalized.
- If no issues are present, return {{"issues":[]}}.
- Return exactly one JSON object, no markdown, no prose."""


def build_prompt(page_data: Dict) -> str:
    return (
        f"URL: {page_data['url']}\n"
        f"Target query: {page_data['target_query']}\n"
        f"Title tag: {page_data.get('title_tag', '') or '(missing)'}\n"
        f"Meta description: {page_data.get('meta_description', '') or '(missing)'}\n"
        f"H1: {page_data.get('h1', '') or '(missing)'}\n"
        f"First paragraph: {page_data.get('first_paragraph', '')[:250]}\n"
        f"Word count: {page_data.get('word_count', 0)}\n"
        f"Headers: {page_data.get('headers', [])}\n"
        f"Schema types: {page_data.get('schema_types', [])}\n"
        f"Has author: {page_data.get('has_author', False)}\n"
        f"Has date: {page_data.get('has_date', False)}\n"
        f"Has sources: {page_data.get('has_sources', False)}\n"
        f"Source count: {page_data.get('source_count', 0)}\n\n"
        "Return your audit as raw JSON only.\n"
        'Example valid response: {"issues":[{"type":"thin_content","severity":"medium"}]}\n'
        'If no issue is clearly supported, return {"issues":[]}.'
    )


def parse_completion(text: str) -> List[Dict]:
    """Extract issues list from model output. Returns [] on any parse failure."""
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match:
            return []
        payload = json.loads(match.group())
        issues = payload.get("issues", [])
        # filter to active types only
        return [i for i in issues if isinstance(i, dict) and i.get("type") in ACTIVE_ISSUE_TYPES]
    except Exception:
        return []


def extract_json_payload(text: str) -> Dict | None:
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        payload = json.loads(match.group())
        return payload if isinstance(payload, dict) else None
    except Exception:
        return None


def normalize_completion_text(completion) -> str:
    """
    Convert TRL/Unsloth completion payloads into a plain string.

    GRPO can pass completions as strings, chat-message dicts, or nested lists
    depending on the backend and generation path.
    """
    if completion is None:
        return ""
    if isinstance(completion, str):
        return completion
    if isinstance(completion, dict):
        for key in ("content", "text"):
            value = completion.get(key)
            if isinstance(value, str):
                return value
            if isinstance(value, list):
                return normalize_completion_text(value)
        return json.dumps(completion, ensure_ascii=False)
    if isinstance(completion, list):
        parts = [normalize_completion_text(item) for item in completion]
        return " ".join(part for part in parts if part).strip()
    return str(completion)


def completion_diagnostics(completion: str, ground_truth_issues: List[Dict]) -> Dict:
    completion = normalize_completion_text(completion)
    payload = extract_json_payload(completion)
    raw_issues = payload.get("issues") if isinstance(payload, dict) else None
    parsed = parse_completion(completion)
    truth = [issue for issue in ground_truth_issues if issue.get("type") in ACTIVE_ISSUE_TYPES]
    flagged_types = {issue["type"] for issue in parsed if isinstance(issue, dict)}
    truth_types = {issue["type"] for issue in truth}
    token_estimate = len(completion.split())
    return {
        "score": score_completion(completion, truth),
        "fp_rate": false_positive_rate(completion, truth),
        "parse_ok": bool(payload is not None and isinstance(raw_issues, list)),
        "empty_prediction": len(flagged_types) == 0,
        "completion_tokens": token_estimate,
        "completion_chars": len(completion),
        "hit_length_cap": token_estimate >= max(1, MAX_GENERATION_TOKENS - 5),
        "false_positive_count": len(flagged_types - truth_types),
        "missed_count": len(truth_types - flagged_types),
    }


def format_reward(completion: str) -> float:
    """Reward valid, constrained JSON before task reward is considered."""
    try:
        match = re.search(r"\{.*\}", completion, re.DOTALL)
        if not match:
            return -0.05
        payload = json.loads(match.group())
        issues = payload.get("issues")
        if not isinstance(issues, list):
            return -0.05

        bonus = 0.05
        for issue in issues:
            if not isinstance(issue, dict):
                return -0.05
            issue_type = issue.get("type")
            severity = issue.get("severity")
            if issue_type not in ACTIVE_ISSUE_TYPES or severity not in {"critical", "high", "medium", "low"}:
                return -0.05
        if issues:
            bonus += 0.05
        return bonus
    except Exception:
        return -0.05


def dense_correctness_reward(completion: str, ground_truth_issues: List[Dict]) -> float:
    """Partial credit: +0.3 per correct issue found, -0.2 per false positive."""
    flagged = parse_completion(completion)
    flagged_types = {i["type"] for i in flagged if isinstance(i, dict)}
    truth_types   = {i["type"] for i in ground_truth_issues if i.get("type") in ACTIVE_ISSUE_TYPES}
    if not truth_types and not flagged_types:
        return 0.3  # correctly identified no issues
    hits = flagged_types & truth_types
    fps  = flagged_types - truth_types
    return 0.3 * len(hits) - 0.2 * len(fps)


def score_completion(completion: str, ground_truth_issues: List[Dict]) -> float:
    flagged = parse_completion(completion)
    return calculate_reward(
        flagged=flagged,
        ground_truth=ground_truth_issues,
        marked_positives=[],
        ground_truth_positives=[],
    )


def false_positive_rate(completion: str, ground_truth_issues: List[Dict]) -> float:
    flagged = parse_completion(completion)
    flagged_types = {i["type"] for i in flagged if isinstance(i, dict)}
    truth_types   = {i["type"] for i in ground_truth_issues}
    if not flagged_types:
        return 0.0
    fps = len(flagged_types - truth_types)
    return fps / len(flagged_types)


def eval_pages_metrics(pages: List[Dict], model, tokenizer) -> Dict:
    scores, fp_rates = [], []
    parse_success, empty_predictions = [], []
    completion_tokens, completion_chars, hit_cap = [], [], []
    per_page_scores = []
    for page in pages:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": build_prompt(page)},
        ]
        inputs = tokenizer.apply_chat_template(
            messages, tokenize=True, add_generation_prompt=True,
            return_tensors="pt"
        ).to(model.device)
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_new_tokens=MAX_GENERATION_TOKENS,
                temperature=0.0,
                do_sample=False,
            )
        completion = tokenizer.decode(outputs[0][inputs.shape[-1]:], skip_special_tokens=True)
        gt = page.get("issues", [])
        diag = completion_diagnostics(completion, gt)
        scores.append(diag["score"])
        fp_rates.append(diag["fp_rate"])
        parse_success.append(float(diag["parse_ok"]))
        empty_predictions.append(float(diag["empty_prediction"]))
        completion_tokens.append(diag["completion_tokens"])
        completion_chars.append(diag["completion_chars"])
        hit_cap.append(float(diag["hit_length_cap"]))
        per_page_scores.append(diag["score"])
    return {
        "avg_reward":   round(float(np.mean(scores)),   3),
        "avg_fp_rate":  round(float(np.mean(fp_rates)), 3),
        "parse_success_rate": round(float(np.mean(parse_success)), 3),
        "empty_prediction_rate": round(float(np.mean(empty_predictions)), 3),
        "avg_completion_tokens": round(float(np.mean(completion_tokens)), 1),
        "avg_completion_chars": round(float(np.mean(completion_chars)), 1),
        "hit_length_cap_rate": round(float(np.mean(hit_cap)), 3),
        "min_reward":   round(float(np.min(scores)),    3),
        "max_reward":   round(float(np.max(scores)),    3),
        "per_page_scores": per_page_scores,
    }


print(f"Model: {MODEL_NAME}")
print(f"Training approach: GRPO via TRL + Unsloth")
print(f"Reward: F1-like score on issue detection, -0.1 per false positive")
print(f"Warm start: broadened SFT foothold before GRPO")
print(f"Experiment mode: {EXPERIMENT_MODE}")
print(f"Generation cap: {MAX_GENERATION_TOKENS} tokens")

# %% [markdown]
# ## Section D — Load Dataset

# %%
def load_all_pages() -> List[Dict]:
    pages = []
    sources = [
        ("data/task1_easy.json", "easy"),
        ("data/task2_medium.json", "medium"),
        ("data/task3_hard.json", "hard"),
    ]
    for fname, difficulty in sources:
        with open(fname) as f:
            for page in json.load(f):
                if "difficulty" not in page:
                    page["difficulty"] = difficulty
                pages.append(page)
    return pages


all_pages = load_all_pages()
if EXPERIMENT_MODE == "easy_only":
    all_pages = [p for p in all_pages if p.get("difficulty") == "easy"]
    print("Dataset selection: easy-only curriculum foothold")
else:
    print("Dataset selection: mixed difficulty")

random.shuffle(all_pages)

split = int(0.8 * len(all_pages))
if len(all_pages) > 1:
    split = min(max(split, 1), len(all_pages) - 1)
train_pages = all_pages[:split]
eval_pages  = all_pages[split:]

print(f"Total pages: {len(all_pages)}")
print(f"Train: {len(train_pages)}  Eval: {len(eval_pages)}")

# %%
# Build HuggingFace dataset for GRPO
from datasets import Dataset

def pages_to_dataset(pages: List[Dict]) -> Dataset:
    rows = []
    for page in pages:
        rows.append({
            "prompt": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": build_prompt(page)},
            ],
            "ground_truth_issues": json.dumps(page.get("issues", [])),
        })
    return Dataset.from_list(rows)


def canonical_issue_output(page: Dict) -> str:
    severity_map = {
        "missing_meta_description": "high",
        "no_direct_answer": "high",
        "thin_content": "medium",
        "no_sources": "medium",
        "no_headers": "medium",
    }
    issues = []
    for issue in page.get("issues", []):
        issue_type = issue["type"]
        if issue_type not in ACTIVE_ISSUE_TYPES:
            continue
        issues.append({
            "type": issue_type,
            "severity": severity_map.get(issue_type, "medium"),
        })
    return json.dumps({"issues": issues}, separators=(",", ":"))


def pages_to_sft_dataset(pages: List[Dict], tokenizer) -> Dataset:
    rows = []
    for page in pages:
        prompt_text = tokenizer.apply_chat_template(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_prompt(page)},
            ],
            tokenize=False,
            add_generation_prompt=True,
        )
        rows.append({
            "text": prompt_text + canonical_issue_output(page)
        })
    return Dataset.from_list(rows)

train_dataset = pages_to_dataset(train_pages)
eval_dataset  = pages_to_dataset(eval_pages)
print(f"Train dataset: {len(train_dataset)} rows")
print(f"Eval dataset:  {len(eval_dataset)} rows")

sft_candidate_pages = [page for page in train_pages if any(
    issue.get("type") in ACTIVE_ISSUE_TYPES for issue in page.get("issues", [])
)]
if not sft_candidate_pages:
    sft_candidate_pages = train_pages
random.shuffle(sft_candidate_pages)
print(f"SFT source pages: {len(sft_candidate_pages)}")

# %% [markdown]
# ## Section E — Baseline LLM Run (Before Training)

# %%
from unsloth import FastLanguageModel
import torch

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=1024,
    load_in_4bit=True,
)
FastLanguageModel.for_inference(model)

print(f"Loaded {MODEL_NAME}")


def run_llm_baseline(pages: List[Dict], model, tokenizer, n: int = None) -> List[float]:
    """Run untrained model on pages and return per-page scores."""
    if n is not None:
        pages = pages[:n]
    scores = []
    for page in pages:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": build_prompt(page)},
        ]
        inputs = tokenizer.apply_chat_template(
            messages, tokenize=True, add_generation_prompt=True,
            return_tensors="pt"
        ).to(model.device)
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_new_tokens=MAX_GENERATION_TOKENS,
                temperature=0.0,
                do_sample=False,
            )
        completion = tokenizer.decode(outputs[0][inputs.shape[-1]:], skip_special_tokens=True)
        score = score_completion(completion, page.get("issues", []))
        scores.append(score)
    return scores


print("Running LLM baseline (eval split) …")
baseline_metrics = eval_pages_metrics(eval_pages, model, tokenizer)
baseline_scores  = baseline_metrics["per_page_scores"]
print(f"LLM baseline  avg={baseline_metrics['avg_reward']:.3f}  "
      f"fp_rate={baseline_metrics['avg_fp_rate']:.3f}  "
      f"parse={baseline_metrics['parse_success_rate']:.3f}  "
      f"hit_cap={baseline_metrics['hit_length_cap_rate']:.3f}")

# record example
example_page = eval_pages[0]
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user",   "content": build_prompt(example_page)},
]
inputs = tokenizer.apply_chat_template(
    messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
).to(model.device)
with torch.no_grad():
    out = model.generate(
        inputs,
        max_new_tokens=MAX_GENERATION_TOKENS,
        temperature=0.0,
        do_sample=False,
    )
baseline_example_output = tokenizer.decode(out[0][inputs.shape[-1]:], skip_special_tokens=True)
baseline_example_score  = score_completion(baseline_example_output, example_page.get("issues", []))
baseline_example_diag = completion_diagnostics(baseline_example_output, example_page.get("issues", []))

print(f"\nBaseline example (page: {example_page['url'][:60]}):")
print(f"  Ground truth issues: {[i['type'] for i in example_page.get('issues', [])]}")
print(f"  Model output: {baseline_example_output[:300]}")
print(f"  Score: {baseline_example_score:.3f}")
print(
    f"  Parse ok: {baseline_example_diag['parse_ok']}  "
    f"tokens: {baseline_example_diag['completion_tokens']}  "
    f"hit_cap: {baseline_example_diag['hit_length_cap']}"
)

# %% [markdown]
# ## Section F — SFT Warm Start + GRPO Training

# %%
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=1024,
    load_in_4bit=True,
)
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=42,
)
sft_dataset = pages_to_sft_dataset(sft_candidate_pages, tokenizer)
print(f"SFT warm-start dataset: {len(sft_dataset)} rows")

# %%
from trl import GRPOConfig, GRPOTrainer, SFTConfig, SFTTrainer


target_sft_examples = 24
if len(sft_dataset) > target_sft_examples:
    sft_dataset = sft_dataset.select(range(target_sft_examples))
    print(f"SFT warm-start dataset capped to {target_sft_examples} rows")

sft_args = SFTConfig(
    output_dir="outputs/round2_sft",
    num_train_epochs=15,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=1,
    learning_rate=2e-5,
    logging_steps=5,
    save_strategy="no",
    report_to="none",
    seed=42,
)

sft_trainer = SFTTrainer(
    model=model,
    args=sft_args,
    train_dataset=sft_dataset,
    processing_class=tokenizer,
)

print("Starting SFT warm start on train-split pages …")
sft_result = sft_trainer.train()
print("SFT warm start complete.")
print(f"  Train loss: {sft_result.training_loss:.4f}")
if sft_result.training_loss > 1.5:
    print("  WARNING: SFT loss still high — warm start may not have worked")
elif sft_result.training_loss < 0.8:
    print("  GOOD: SFT looks strong enough for GRPO refinement")


_reward_log: List[Dict] = []
_generation_log: List[Dict] = []  # sampled completions for drift inspection

def reward_fn(completions: List[str], ground_truth_issues: List[str], **kwargs) -> List[float]:
    rewards = []
    for completion, gt_json in zip(completions, ground_truth_issues):
        completion = normalize_completion_text(completion)
        gt_issues = json.loads(gt_json)
        correctness = dense_correctness_reward(completion, gt_issues)
        fmt         = format_reward(completion)

        flagged = parse_completion(completion)
        flagged_types = {i["type"] for i in flagged if isinstance(i, dict)}
        truth_types   = {i["type"] for i in gt_issues if i.get("type") in ACTIVE_ISSUE_TYPES}
        fp_count      = len(flagged_types - truth_types)
        fp_penalty    = -0.2 * fp_count
        token_estimate = len(completion.split())
        parse_ok = extract_json_payload(completion) is not None

        total = max(0.0, correctness + fmt)
        rewards.append(total)
        _reward_log.append({
            "correctness": round(correctness, 3),
            "format":      round(fmt, 3),
            "fp_penalty":  round(fp_penalty, 3),
            "total":       round(total, 3),
            "tokens":      token_estimate,
            "parse_ok":    parse_ok,
            "hit_cap":     token_estimate >= max(1, MAX_GENERATION_TOKENS - 5),
        })

    # print decomposed reward every 8 calls
    if len(_reward_log) % 8 == 0 and _reward_log:
        recent = _reward_log[-8:]
        print(
            f"  [reward] correctness={np.mean([r['correctness'] for r in recent]):.3f}"
            f"  format={np.mean([r['format'] for r in recent]):.3f}"
            f"  fp_penalty={np.mean([r['fp_penalty'] for r in recent]):.3f}"
            f"  total={np.mean([r['total'] for r in recent]):.3f}"
            f"  tokens={np.mean([r['tokens'] for r in recent]):.1f}"
            f"  parse_ok={np.mean([float(r['parse_ok']) for r in recent]):.2f}"
            f"  hit_cap={np.mean([float(r['hit_cap']) for r in recent]):.2f}"
        )

    # sample one raw completion every 20 calls — catch reward hacking before it compounds
    if len(_reward_log) % 20 == 0 and completions:
        sample = normalize_completion_text(completions[0])
        gt_sample = json.loads(ground_truth_issues[0])
        truth_preview = [i["type"] for i in gt_sample if i.get("type") in ACTIVE_ISSUE_TYPES]
        print(f"  [generation sample]")
        print(f"    truth:      {truth_preview}")
        print(f"    completion: {sample[:120]}")
        _generation_log.append({"step": len(_reward_log), "truth": truth_preview, "completion": sample[:200]})

    return rewards


training_args = GRPOConfig(
    output_dir="outputs/round2_grpo",
    num_train_epochs=5,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    num_generations=8,
    max_completion_length=80,    # short completions force crisp JSON, not wall-of-text
    temperature=0.7,             # rollout diversity for GRPO variance
    learning_rate=2e-5,
    lr_scheduler_type="cosine",
    warmup_ratio=0.1,
    logging_steps=2,
    save_steps=50,
    report_to="none",
    seed=42,
)

trainer = GRPOTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    reward_funcs=reward_fn,
    processing_class=tokenizer,
)

# %%
print("Starting GRPO training …")
train_result = trainer.train()
print("Training complete.")
print(f"  Steps: {train_result.global_step}")
print(f"  Final loss: {train_result.training_loss:.4f}")
reward_logs = [e for e in trainer.state.log_history if "reward" in e]
if reward_logs:
    reward_values = [e["reward"] for e in reward_logs]
    print(
        f"  Reward signal: min={min(reward_values):.3f} "
        f"max={max(reward_values):.3f} std={float(np.std(reward_values)):.3f}"
    )

# %% [markdown]
# ## Section G — Post-Training Evaluation

# %%
FastLanguageModel.for_inference(model)

print("Running post-training evaluation on eval split …")
trained_metrics = eval_pages_metrics(eval_pages, model, tokenizer)
trained_scores  = trained_metrics["per_page_scores"]
print(f"Trained model  avg={trained_metrics['avg_reward']:.3f}  "
      f"fp_rate={trained_metrics['avg_fp_rate']:.3f}  "
      f"parse={trained_metrics['parse_success_rate']:.3f}  "
      f"hit_cap={trained_metrics['hit_length_cap_rate']:.3f}")

# trained example output
inputs = tokenizer.apply_chat_template(
    messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
).to(model.device)
with torch.no_grad():
    out = model.generate(
        inputs,
        max_new_tokens=MAX_GENERATION_TOKENS,
        temperature=0.0,
        do_sample=False,
    )
trained_example_output = tokenizer.decode(out[0][inputs.shape[-1]:], skip_special_tokens=True)
trained_example_score  = score_completion(trained_example_output, example_page.get("issues", []))
trained_example_diag = completion_diagnostics(trained_example_output, example_page.get("issues", []))

print(f"\nTrained example (same page as baseline):")
print(f"  Ground truth issues: {[i['type'] for i in example_page.get('issues', [])]}")
print(f"  Model output: {trained_example_output[:300]}")
print(f"  Score: {trained_example_score:.3f}")
print(
    f"  Parse ok: {trained_example_diag['parse_ok']}  "
    f"tokens: {trained_example_diag['completion_tokens']}  "
    f"hit_cap: {trained_example_diag['hit_length_cap']}"
)

# %% [markdown]
# ## Section H — Save Evidence

# %%
Path("artifacts").mkdir(exist_ok=True)

# ── Comparison table ──────────────────────────────────────────────────────────
comparison = {
    "heuristic_baseline":  {"avg_reward": round(float(np.mean(heuristic_scores)), 3), "avg_fp_rate": "n/a"},
    "llm_before_training": baseline_metrics,
    "llm_after_training":  trained_metrics,
}
with open("artifacts/round2_comparison.json", "w") as f:
    json.dump(comparison, f, indent=2)
print("Comparison table:")
for k, v in comparison.items():
    print(f"  {k}: {v}")

# ── Reward bar chart ──────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 4))
labels = ["Heuristic\nbaseline", "LLM\nbefore training", "LLM\nafter training"]
values = [
    comparison["heuristic_baseline"]["avg_reward"],
    comparison["llm_before_training"]["avg_reward"],
    comparison["llm_after_training"]["avg_reward"],
]
colors = ["#6c757d", "#dc3545", "#198754"]
bars = ax.bar(labels, values, color=colors, width=0.5, zorder=3)
ax.set_ylim(0, 1.05)
ax.set_ylabel("Average reward (F1-like score)")
ax.set_title("GEO Audit Agent — Before vs After GRPO Training")
ax.grid(axis="y", alpha=0.3, zorder=0)
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width() / 2, val + 0.02,
            f"{val:.3f}", ha="center", va="bottom", fontweight="bold")
plt.tight_layout()
plt.savefig("artifacts/round2_comparison.png", dpi=150)
plt.show()
print("Saved: artifacts/round2_comparison.png")

# ── Per-page score distribution ───────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 4))
bins = np.linspace(0, 1, 15)
ax.hist(baseline_scores, bins=bins, alpha=0.6, label="Before training", color="#dc3545")
ax.hist(trained_scores,  bins=bins, alpha=0.6, label="After training",  color="#198754")
ax.set_xlabel("Reward score")
ax.set_ylabel("Page count")
ax.set_title("Score distribution — Before vs After GRPO Training")
ax.legend()
plt.tight_layout()
plt.savefig("artifacts/round2_score_distribution.png", dpi=150)
plt.show()
print("Saved: artifacts/round2_score_distribution.png")

# ── Training reward curve ─────────────────────────────────────────────────────
if hasattr(trainer.state, "log_history") and trainer.state.log_history:
    log = [e for e in trainer.state.log_history if "reward" in e]
    if log:
        steps   = [e["step"]   for e in log]
        rewards = [e["reward"] for e in log]
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(steps, rewards, color="#0d6efd", linewidth=1.5)
        ax.set_xlabel("Training step")
        ax.set_ylabel("Mean batch reward")
        ax.set_title("GRPO Training Reward Curve")
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig("artifacts/round2_training_curve.png", dpi=150)
        plt.show()
        print("Saved: artifacts/round2_training_curve.png")

# ── Before / after example transcript ────────────────────────────────────────
transcript = {
    "page_url": example_page["url"],
    "target_query": example_page["target_query"],
    "ground_truth_issues": [i["type"] for i in example_page.get("issues", [])],
    "before": {
        "output": baseline_example_output,
        "score":  round(baseline_example_score, 3),
    },
    "after": {
        "output": trained_example_output,
        "score":  round(trained_example_score, 3),
    },
}
with open("artifacts/round2_example_transcript.json", "w") as f:
    json.dump(transcript, f, indent=2)
print("Saved: artifacts/round2_example_transcript.json")

if _generation_log:
    with open("artifacts/round2_generation_samples.json", "w") as f:
        json.dump(_generation_log, f, indent=2)
    print(f"Saved: artifacts/round2_generation_samples.json ({len(_generation_log)} samples)")

print("\nAll artifacts saved to artifacts/")
print("\nSummary:")
print(f"  Heuristic baseline:  {comparison['heuristic_baseline']}")
print(f"  LLM before training: {comparison['llm_before_training']}")
print(f"  LLM after training:  {comparison['llm_after_training']}")
delta = comparison["llm_after_training"]["avg_reward"] - comparison["llm_before_training"]["avg_reward"]
print(f"  Delta (LLM):         {delta:+.3f}")
