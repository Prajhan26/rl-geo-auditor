import json
import os
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from openai import OpenAI
from server.environment import GeoAuditEnvironment
from server.models import GeoAuditAction, GeoAuditObservation, PageData


SEVERITY_ORDER = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}

HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "Qwen/Qwen2.5-72B-Instruct"
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")
BENCHMARK_NAME = os.getenv("BENCHMARK_NAME") or "geo-audit-env"
TASK_SEQUENCE = ("easy", "medium", "hard")
MAX_MODEL_TOKENS = 220
TEMPERATURE = 0.0
SUCCESS_SCORE_THRESHOLD = 0.5
MIN_SUBMISSION_SCORE = 0.001
MAX_SUBMISSION_SCORE = 0.999

SYSTEM_PROMPT = """
You are auditing a webpage inside a GEO environment.
Pick exactly one next action from the provided candidate actions.
Return only valid JSON with these keys:
- action_type
- issue_type
- positive_type
- severity
- details

Rules:
- Choose only one action from the candidate list.
- Prefer checking evidence before flagging issues.
- If the likely issues are already flagged, submit_report.
- Do not invent issue types or action types.
""".strip()


@dataclass
class IssueCandidate:
    """A possible GEO issue inferred from the page signals."""

    issue_type: str
    severity: str
    reason: str
    confidence: float
    required_checks: Set[str]


def tokenize(text: str) -> Set[str]:
    cleaned = []
    for char in text.lower():
        cleaned.append(char if char.isalnum() or char.isspace() else " ")
    return {
        normalize_token(token)
        for token in "".join(cleaned).split()
        if len(token) > 2
    }


def normalize_token(token: str) -> str:
    for suffix in ("ing", "ed", "es", "s"):
        if token.endswith(suffix) and len(token) - len(suffix) >= 4:
            return token[: -len(suffix)]
    return token


def overlap_ratio(query: str, text: str) -> float:
    query_terms = tokenize(query)
    text_terms = tokenize(text)
    if not query_terms:
        return 0.0

    matched_terms = 0
    for query_term in query_terms:
        if any(
            query_term == text_term
            or query_term.startswith(text_term)
            or text_term.startswith(query_term)
            for text_term in text_terms
        ):
            matched_terms += 1

    return matched_terms / len(query_terms)


def looks_like_direct_answer(query: str, paragraph: str) -> bool:
    starters = {"to", "you", "stake", "ethereum", "the", "best", "how"}
    fluff_markers = {
        "welcome",
        "team",
        "company",
        "mission",
        "founded",
        "enthusiast",
    }
    paragraph_terms = tokenize(paragraph)
    overlap = overlap_ratio(query, paragraph)
    has_fluff_intro = bool(paragraph_terms & fluff_markers)
    return overlap >= 0.55 or (
        bool(paragraph_terms & starters) and overlap >= 0.34 and not has_fluff_intro
    )


def looks_like_buried_answer(query: str, paragraph: str) -> bool:
    paragraph_terms = tokenize(paragraph)
    fluff_markers = {
        "welcome",
        "newsletter",
        "platform",
        "sponsor",
        "company",
        "introduce",
    }
    overlap = overlap_ratio(query, paragraph)
    return overlap >= 0.25 and bool(paragraph_terms & fluff_markers)


def build_issue_candidates(page: PageData) -> List[IssueCandidate]:
    candidates: List[IssueCandidate] = []

    title_overlap = overlap_ratio(page.target_query, page.title_tag)
    meta_overlap = overlap_ratio(page.target_query, page.meta_description)
    paragraph_overlap = overlap_ratio(page.target_query, page.first_paragraph)
    schema_types = set(page.schema_types)
    headers_lower = [header.lower() for header in page.headers]
    query_lower = page.target_query.lower()
    title_lower = page.title_tag.lower()
    meta_lower = page.meta_description.lower()
    url_lower = page.url.lower()
    faq_query = "faq" in query_lower
    faq_like_page = faq_query or any("faq" in header for header in headers_lower)
    generic_site_title = title_overlap == 0.0 and any(
        term in title_lower for term in ("blog", "news", "company")
    )
    how_to_like_query = (
        query_lower.startswith("how to")
        or any("step" in header or "how to" in header for header in headers_lower)
    )
    docs_like_page = any(
        token in url_lower or token in title_lower
        for token in ("docs.", "/docs/", " lido docs", "reference", "contracts")
    )
    staking_hub_page = any(
        token in url_lower
        for token in (
            "ethereum.org/staking/",
            "ethereum.org/staking$",
            "ethereum.org/staking?",
        )
    )
    staking_author_gap_page = any(
        token in url_lower
        for token in (
            "ethereum.org/staking/",
            "ethereum.org/staking/solo/",
            "ethereum.org/staking/pools/",
        )
    )
    author_visibility_unreliable = staking_author_gap_page and "withdrawals" not in url_lower
    article_like_page = page.word_count >= 120 and (
        bool(page.headers)
        or "guide" in query_lower
        or "overview" in query_lower
        or "faq" in query_lower
        or "guide" in title_lower
        or "overview" in title_lower
    )
    article_schema_likely = (
        page.word_count >= 120
        and bool(page.headers)
        and not faq_like_page
        and "overview" not in query_lower
        and "overview" not in title_lower
        and not docs_like_page
        and (not page.has_author or not page.has_date or page.source_count < 4)
    )

    if not page.title_tag:
        candidates.append(
            IssueCandidate(
                issue_type="missing_title_tag",
                severity="critical",
                reason="The page has no title tag at all.",
                confidence=0.99,
                required_checks=set(),
            )
        )
    elif title_overlap < 0.26 or len(page.title_tag) < 12 or title_lower in {
        "blog post",
        "article",
        "home",
    }:
        title_confidence = 0.62
        strong_explainer_title = (
            title_lower.startswith("what is ")
            or "complete guide" in title_lower
            or ("guide" in title_lower and title_overlap >= 0.18)
        )
        if len(page.title_tag) < 12 or title_overlap < 0.15:
            title_confidence = 0.8
        if not generic_site_title and not docs_like_page and not strong_explainer_title:
            candidates.append(
                IssueCandidate(
                    issue_type="weak_title_tag",
                    severity="medium",
                    reason="The title tag is too generic or poorly aligned with the target query.",
                    confidence=title_confidence,
                    required_checks=set(),
                )
            )

    if not page.meta_description:
        candidates.append(
            IssueCandidate(
                issue_type="missing_meta_description",
                severity="critical",
                reason="The page is missing a meta description.",
                confidence=0.99,
                required_checks=set(),
            )
        )
    elif (
        len(page.meta_description) < 25
        or meta_lower.strip() in {"- source code", "source code"}
        or "learn about" in meta_lower
        or ("welcome" in meta_lower and meta_overlap < 0.35)
        or (meta_overlap < 0.12 and len(page.meta_description) < 60)
    ):
        candidates.append(
            IssueCandidate(
                issue_type="weak_meta_description",
                severity="medium",
                reason="The meta description is present but not strong for the target query.",
                confidence=0.7,
                required_checks=set(),
            )
        )

    if not page.headers:
        candidates.append(
            IssueCandidate(
                issue_type="no_headers",
                severity="high",
                reason="The page has no visible section headers, so it reads like a wall of text.",
                confidence=0.95,
                required_checks={"check_headers"},
            )
        )

    if page.word_count < 300:
        candidates.append(
            IssueCandidate(
                issue_type="thin_content",
                severity="medium",
                reason=f"The page has only {page.word_count} words, which is thin for this type of query.",
                confidence=0.9,
                required_checks={"check_word_count"},
            )
        )

    if (not page.has_author or author_visibility_unreliable) and page.word_count >= 300:
        candidates.append(
            IssueCandidate(
                issue_type="no_author",
                severity="medium",
                reason="The page does not show an author attribution.",
                confidence=0.76 if staking_hub_page else (0.72 if article_like_page else 0.58),
                required_checks={"check_trust_signals"},
            )
        )

    if not page.has_date and page.word_count >= 300:
        candidates.append(
            IssueCandidate(
                issue_type="no_date",
                severity="medium",
                reason="The page does not show a publish or update date.",
                confidence=0.74 if article_like_page else 0.6,
                required_checks={"check_trust_signals"},
            )
        )

    low_source_support = (
        faq_like_page
        or page.word_count >= 800
        or (page.word_count >= 500 and "faq" in title_lower)
    ) and (
        (not page.has_sources) or page.source_count == 0 or (
            page.word_count >= 1500 and page.source_count < 2
        )
    ) and not docs_like_page
    if low_source_support:
        candidates.append(
            IssueCandidate(
                issue_type="no_sources",
                severity="low",
                reason="The page does not show supporting citations or references.",
                confidence=0.76 if faq_like_page or page.word_count >= 1500 else 0.66,
                required_checks={"check_sources"},
            )
        )

    should_expect_direct_answer = (
        not faq_query
        and not docs_like_page
        and title_overlap < 0.8
        and meta_overlap < 0.45
        and (
            paragraph_overlap < 0.18
            or (
                paragraph_overlap < 0.28
                and title_overlap < 0.2
                and meta_overlap < 0.2
                and page.word_count < 1200
            )
        )
    )
    if should_expect_direct_answer and not looks_like_direct_answer(
        page.target_query, page.first_paragraph
    ):
        issue_type = (
            "buried_answer"
            if looks_like_buried_answer(page.target_query, page.first_paragraph)
            else "no_direct_answer"
        )
        candidates.append(
            IssueCandidate(
                issue_type=issue_type,
                severity="high" if issue_type == "buried_answer" else "critical",
                reason="The opening paragraph does not clearly answer the target query up front.",
                confidence=0.84 if issue_type == "buried_answer" else (
                    0.87 if paragraph_overlap < 0.34 else 0.62
                ),
                required_checks=set(),
            )
        )

    if (
        how_to_like_query
        and page.word_count >= 500
        and "HowTo" not in schema_types
        and "FAQPage" not in schema_types
        and "Answer" not in schema_types
        and not docs_like_page
    ):
        candidates.append(
            IssueCandidate(
                issue_type="missing_howto_schema",
                severity="high",
                reason="This looks like a how-to page, but it is missing HowTo schema.",
                confidence=0.82,
                required_checks={"check_schema", "check_headers"},
            )
        )

    if any("faq" in header or "question" in header for header in headers_lower) and "FAQPage" not in schema_types:
        candidates.append(
            IssueCandidate(
                issue_type="missing_faq_schema",
                severity="high",
                reason="The page has FAQ-like sections but no FAQPage schema.",
                confidence=0.86,
                required_checks={"check_schema", "check_headers"},
            )
        )

    if article_schema_likely and "Article" not in schema_types:
        candidates.append(
            IssueCandidate(
                issue_type="missing_article_schema",
                severity="high",
                reason="This is article-style content but there is no Article schema.",
                confidence=0.62 if page.word_count < 400 else 0.55,
                required_checks=set(),
            )
        )

    return candidates


def plan_actions(observation: GeoAuditObservation) -> List[GeoAuditAction]:
    """
    Build an explainable audit plan from the current observation.

    This is still heuristic, not learned.
    The important upgrade is that actions now come from page evidence rather
    than a hard-coded one-size-fits-all script.
    """

    page = observation.page
    candidates = build_issue_candidates(page)
    ranked_candidates = sorted(
        candidates,
        key=lambda item: (item.confidence, SEVERITY_ORDER[item.severity]),
        reverse=True,
    )

    max_steps = observation.max_steps
    remaining_budget = max_steps - 1
    selected_candidates: List[IssueCandidate] = []
    selected_checks_set: Set[str] = set()

    for candidate in ranked_candidates:
        new_checks = candidate.required_checks - selected_checks_set
        action_cost = len(new_checks) + 1
        if action_cost <= remaining_budget:
            selected_candidates.append(candidate)
            selected_checks_set.update(candidate.required_checks)
            remaining_budget -= action_cost

    selected_checks = sorted(selected_checks_set)

    actions: List[GeoAuditAction] = [
        GeoAuditAction(action_type=check_name) for check_name in selected_checks
    ]

    for candidate in selected_candidates:
        actions.append(
            GeoAuditAction(
                action_type="flag_issue",
                issue_type=candidate.issue_type,
                severity=candidate.severity,
                details=candidate.reason,
            )
        )

    actions.append(GeoAuditAction(action_type="submit_report"))
    return actions


def checked_action_names(observation: GeoAuditObservation) -> Set[str]:
    checked = observation.checked
    names: Set[str] = set()
    if checked.title_tag is not None:
        names.add("check_title_tag")
    if checked.meta_description is not None:
        names.add("check_meta_description")
    if checked.headers is not None:
        names.add("check_headers")
    if checked.schema is not None:
        names.add("check_schema")
    if checked.direct_answer is not None:
        names.add("check_direct_answer")
    if checked.content_structure is not None:
        names.add("check_content_structure")
    if checked.word_count is not None:
        names.add("check_word_count")
    if checked.trust_signals is not None:
        names.add("check_trust_signals")
    if checked.sources is not None:
        names.add("check_sources")
    return names


def action_to_payload(action: GeoAuditAction) -> Dict[str, str]:
    payload = {"action_type": action.action_type}
    if action.issue_type:
        payload["issue_type"] = action.issue_type
    if action.positive_type:
        payload["positive_type"] = action.positive_type
    if action.severity:
        payload["severity"] = action.severity
    if action.details:
        payload["details"] = action.details
    return payload


def action_to_string(action: GeoAuditAction) -> str:
    return json.dumps(action_to_payload(action), separators=(",", ":"))


def build_candidate_actions(observation: GeoAuditObservation) -> List[GeoAuditAction]:
    planned = plan_actions(observation)
    checked = checked_action_names(observation)
    flagged = {issue["type"] for issue in observation.flagged_issues}

    candidates: List[GeoAuditAction] = []
    for action in planned:
        if action.action_type.startswith("check_") and action.action_type in checked:
            continue
        if action.action_type == "flag_issue" and action.issue_type in flagged:
            continue
        candidates.append(action)

    if not candidates:
        candidates.append(GeoAuditAction(action_type="submit_report"))

    return candidates[:6]


def build_user_prompt(
    observation: GeoAuditObservation,
    candidate_actions: List[GeoAuditAction],
    task_difficulty: str,
) -> str:
    page = observation.page
    candidate_lines = "\n".join(
        f"- {action_to_string(action)}" for action in candidate_actions
    )
    return (
        f"Task difficulty: {task_difficulty}\n"
        f"Page URL: {page.url}\n"
        f"Target query: {page.target_query}\n"
        f"Current step: {observation.step_count}/{observation.max_steps}\n"
        f"Last environment message: {observation.message}\n"
        f"Already flagged issues: {[item['type'] for item in observation.flagged_issues]}\n"
        f"Already marked positives: {[item['type'] for item in observation.marked_positives]}\n"
        f"Available candidate actions:\n{candidate_lines}\n"
        "Return exactly one JSON object copied from the candidate list."
    )


def parse_action_response(
    content: str,
    candidate_actions: List[GeoAuditAction],
) -> Optional[GeoAuditAction]:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return None

    chosen_type = payload.get("action_type")
    chosen_issue = payload.get("issue_type")
    chosen_positive = payload.get("positive_type")

    for candidate in candidate_actions:
        if (
            candidate.action_type == chosen_type
            and candidate.issue_type == chosen_issue
            and candidate.positive_type == chosen_positive
        ):
            return candidate
    return None


def choose_action_with_model(
    client: OpenAI,
    observation: GeoAuditObservation,
    task_difficulty: str,
) -> tuple[GeoAuditAction, Optional[str]]:
    candidate_actions = build_candidate_actions(observation)
    fallback_action = candidate_actions[0]
    user_prompt = build_user_prompt(observation, candidate_actions, task_difficulty)

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_MODEL_TOKENS,
        )
        content = (completion.choices[0].message.content or "").strip()
        parsed_action = parse_action_response(content, candidate_actions)
        if parsed_action is not None:
            return parsed_action, None
        return fallback_action, "invalid_model_action"
    except Exception as exc:  # pragma: no cover - runtime/network dependent
        return fallback_action, str(exc)


def log_start(task: str, env_name: str, model: str) -> None:
    print(f"[START] task={task} env={env_name} model={model}", flush=True)


def log_step(step: int, action: GeoAuditAction, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action_to_string(action)} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{item:.2f}" for item in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


def normalize_submission_score(score: float) -> float:
    return min(MAX_SUBMISSION_SCORE, max(MIN_SUBMISSION_SCORE, score))


def run_episode(client: OpenAI, task_difficulty: str) -> float:
    env = GeoAuditEnvironment()
    observation = env.reset(task_difficulty=task_difficulty)
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=task_difficulty, env_name=BENCHMARK_NAME, model=MODEL_NAME)

    try:
        for step in range(1, observation.max_steps + 1):
            if observation.done:
                break

            action, action_error = choose_action_with_model(
                client,
                observation,
                task_difficulty,
            )
            observation = env.step(action)

            rewards.append(observation.reward)
            steps_taken = step
            log_step(
                step=step,
                action=action,
                reward=observation.reward,
                done=observation.done,
                error=action_error,
            )

            if observation.done:
                break

        score = normalize_submission_score(observation.reward)
        success = score >= SUCCESS_SCORE_THRESHOLD
    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    return score


if __name__ == "__main__":
    random.seed(0)
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    for difficulty in TASK_SEQUENCE:
        run_episode(client=client, task_difficulty=difficulty)
