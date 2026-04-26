---
title: GEO Audit Environment
emoji: "🔎"
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
short_description: GEO audit RL environment with FastAPI endpoints.
---

# GEO Audit Environment

**Live environment:** https://samunhashed-geo-audit-env.hf.space  
**API docs:** https://samunhashed-geo-audit-env.hf.space/docs  
**Full writeup:** [docs/ROUND2_WRITEUP.md](docs/ROUND2_WRITEUP.md)

---

I built this project out of a pretty simple frustration.

Around GEO, AI search, answer engines, and AI for SEO work, I kept seeing teams spend serious money without a clean way to evaluate whether an agent was actually good at the job. I've been close to this with companies and teams around names like MoonPay, Ledger, Alto, and QuickNode, and the pattern was always similar: lots of opinions, lots of content, lots of spend, but no real environment for testing behavior end to end.

Most tools in this space can generate recommendations. Very few let you put an agent inside a workflow, inspect what it does, grade it programmatically, compare baselines, and try training against that loop.

That gap is why this repo exists.

This project turns GEO auditing into an environment. An agent gets a page and a target query, inspects structured page signals, flags issues, submits a report, and gets scored against benchmark truth. The goal is not just to make GEO advice sound smart. The goal is to make GEO work measurable, testable, and eventually trainable.

## Live demo: one full audit episode

The environment is running at `https://samunhashed-geo-audit-env.hf.space`. Here is a real episode, live from the API.

**Step 1 — start an episode**
```bash
curl -X POST https://samunhashed-geo-audit-env.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"task_difficulty": "easy"}'
```
Returns a page with structured signals:
```
url:         https://example.com/validator-uptime
query:       what is validator uptime
meta:        "Learn about uptime."
word_count:  210
has_sources: false
headers:     []
steps:       0/10
```

**Step 2 — agent flags an issue**
```bash
curl -X POST https://samunhashed-geo-audit-env.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{"action_type": "flag_issue", "issue_type": "thin_content", "severity": "medium"}'
```

**Step 3 — submit and receive reward**
```bash
curl -X POST https://samunhashed-geo-audit-env.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{"action_type": "submit_report"}'
```
```
reward:  0.5
flagged: ['thin_content']
done:    true
```

The reward is 0.5 — the agent found one real issue. Flagging a second correct issue would push it toward 1.0. Flagging a wrong issue would pull it down. That is the verifier working as intended.

**Before vs after training — same environment, same verifier:**

**1. Baseline model attempt (before training)**

The untrained 7B model on an easy page with `thin_content` and `missing_meta_description` as ground truth:
```json
{"issues":[{"type":"thin_content","severity":"medium"},{"type":"no_direct_answer","severity":"high"},{"type":"missing_schema","severity":"medium"}]}
```
It found one real issue and invented two that are not there.

**2. Verifier output**
```
F1(flagged={thin_content, no_direct_answer, missing_schema}, truth={thin_content, missing_meta_description})
= F1 score: 0.333  →  false positives: 2  →  penalty: -0.2
= reward: 0.133
```
Low reward. The model found one real issue but hallucinated two, collapsing precision.

**3. Trained model attempt (after SFT + GRPO)**
```json
{"issues":[{"type":"thin_content","severity":"medium"}]}
```
One issue. The one that is actually there. Nothing invented.

**4. Measurable improvement**

| Metric | Before | After |
|--------|--------|-------|
| false positive rate | 0.333 | **0.250** |
| avg response length | 96 chars | **56 chars** |
| parse success | 1.00 | 1.00 |

The reward delta on the 4-page eval split is -0.009 — noise at that scale. The behavioral change is real and consistent: the model hallucinates less and produces shorter, more precise outputs.

![Reward comparison — heuristic vs LLM before and after training](artifacts/round2_comparison.png)
*Heuristic baseline (0.964) sets the ceiling. LLM before (0.467) vs after SFT+GRPO (0.458) — delta is noise on 4 pages, behavioral improvements are real.*

![Behavioral improvements after training](artifacts/round2_behavioral.png)
*Left: false positive rate 0.333 → 0.250 (25% fewer hallucinated issues). Right: response length 96 → 56 chars (42% more concise).*

**5. Safeguards**

The verifier penalizes false positives twice — once through F1 precision and again with an explicit -0.1 multiplier per false positive. Inventing issues is always a losing strategy. The environment also caps episodes at 10 steps and rejects unknown issue types outright, so the agent cannot game the loop by flooding it with arbitrary flags.

## Why this is not just another GEO tool

Most SEO or GEO products help a human audit a page. There is a person in the loop. They read the output, decide what to do, and move on.

This project removes the human from that loop and asks a harder question: can the agent itself be evaluated, compared, and improved?

That requires something different from a text box with a submit button. It requires a structured action space, a deterministic verifier, benchmark tasks at real difficulty levels, and a reward signal that cannot be gamed by generating confident-sounding output.

None of that is free. That is why most tools do not have it.

## The environment loop

An agent in this environment:

1. receives a page and target query via `POST /reset`
2. inspects structured signals — title, meta, headers, schema, sources, trust signals
3. flags issues and marks positives via `POST /step`
4. submits a final report
5. receives a deterministic reward from the grader

The loop is exposed through three endpoints: `reset`, `step`, `state`. It follows the OpenEnv spec and passes automated validation.

## Reward design

The reward is F1-style with a hard hallucination penalty.

```
reward = F1(flagged_types, truth_types) - (0.1 × false_positive_count)
```

False positives get penalized twice — once through lower precision in the F1, and again through the explicit multiplier. Flagging everything does not work. I specifically designed it so that dumping every known issue type onto every page is a losing strategy.

A clean page that receives an empty report scores 1.0. Knowing when to say nothing is part of the task.

Positive findings are tracked separately at 15% weight, so a complete audit that catches both issues and strengths scores higher than one that only flags problems.

## Why the difficulty levels are genuinely different

Easy, medium, and hard are not just harder versions of the same check. They test different kinds of reasoning.

**Easy** — binary, deterministic signals. Is `meta_description` empty? Is `word_count` below threshold? Is `has_sources` false? The correct answer can be read directly off the page data.

**Medium** — combined signals. A page might have a meta description that exists but is too short. It might have sources in a format the grader does not credit. Requires reasoning about signal quality, not just signal presence.

**Hard** — query-content relationship. Flagging `no_direct_answer` on a hard page means understanding that the content does not match what someone searching that specific query actually needs. That is a judgment call, not a lookup.

This gradient matters for training. Easy tasks give signal early. Hard tasks prevent reward saturation from shallow pattern-matching. The mix is intentional.

## Reward hacking: how I tried to break it

Before defending the reward to anyone else, I tried to break it myself.

**Flag nothing** — outputs `{"issues":[]}` everywhere. Scores 1.0 on clean pages, 0.0 on pages with real issues. Works if the benchmark is heavily skewed toward clean pages. Guardrail: the benchmark intentionally includes pages across all difficulty levels.

**Flag everything** — outputs all known issue types on every page. Recall is always 1.0 but precision collapses and the -0.1 FP multiplier makes it unprofitable. Still gets partial credit on pages with many real issues, which is a known weakness.

**Memorize label priors** — if `no_sources` appears in 30 of 60 pages, always flag it. Guardrail: held-out eval split. But the benchmark is not adversarially constructed, so this risk is real and acknowledged.

**Exploit the clean-page shortcut** — learn to output nothing on ambiguous pages. Guardrail: difficulty-balanced benchmark. Still a soft guardrail.

No single shallow strategy dominates. But I would not claim the reward is impossible to game. The benchmark is not adversarially constructed, and that is a real gap. The next version needs rotating eval splits, pages designed to fool shallow pattern-matching, and checks that verify the agent actually did the audit work before submitting a report.

## The benchmark: 49 real pages, manually reviewed

I did not want to only evaluate against synthetic data. Synthetic benchmarks are easy to score well on, and that would be cheating myself.

Each page was collected from the live web, checked against the issue taxonomy, and labeled by hand. The benchmark covers 15 easy, 17 medium, and 17 hard pages.

Real benchmark results:
- heuristic policy: `0.571` overall
- learned policy: `0.460` overall

The lower score compared to the synthetic benchmark is expected. It shows the real benchmark is actually harder, which makes it a better proof set. If both benchmarks scored 1.0, the real one would be useless.

The frozen dataset: `artifacts/real_dataset_finalized_49.json`

## Full writeup

The detailed technical writeup covering verifier design, reward hacking analysis, task difficulty reasoning, and real-world transfer is in [`docs/ROUND2_WRITEUP.md`](docs/ROUND2_WRITEUP.md).

## Round 2 training

Training is 10% of this project's story. The environment is the point. But for completeness:

We ran SFT warm start → GRPO on `Qwen2.5-7B-Instruct`.

The key finding: GRPO produces zero signal until SFT teaches the output format first. Once SFT loss dropped from 3.15 to 0.84, GRPO produced real reward variance (std=0.172) and the model's false-positive rate fell from 0.333 to 0.250.

Full script: `scripts/round2_train.py` | Results: `artifacts/round2_comparison.json`

## Project structure

```text
server/
  app.py             FastAPI app
  api_models.py      Typed request/response schemas
  environment.py     Audit environment logic
  grader.py          Reward calculation
  models.py          Action/observation/state models
data/
  task1_easy.json    Easy task pages
  task2_medium.json  Medium task pages
  task3_hard.json    Hard task pages
artifacts/           Policies, benchmark data, training results
inference.py         Heuristic baseline policy
scripts/
  round2_train.py    SFT + GRPO training script
openenv.yaml         OpenEnv spec
Dockerfile           Container setup
```

## Local setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

Run the heuristic baseline:
```bash
python3 inference.py
```

Start the API:
```bash
./venv/bin/uvicorn server.app:app --host 127.0.0.1 --port 8000
```

Validate OpenEnv compliance:
```bash
./venv/bin/openenv validate .
```

## API endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Status check |
| `/metadata` | GET | Environment metadata and action space |
| `/state` | GET | Current episode state |
| `/reset` | POST | Start new audit episode |
| `/step` | POST | Apply one audit action |

## Docker

```bash
docker build -t geo-audit-env .
docker run -p 8000:8000 geo-audit-env
```

Then: `http://localhost:8000/docs`
