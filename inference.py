from dataclasses import dataclass
from typing import Dict, List, Set

from server.environment import GeoAuditEnvironment
from server.models import GeoAuditAction, GeoAuditObservation, PageData


SEVERITY_ORDER = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}


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
    faq_query = "faq" in query_lower
    faq_like_page = faq_query or any("faq" in header for header in headers_lower)
    generic_site_title = title_overlap == 0.0 and any(
        term in title_lower for term in ("blog", "news", "company")
    )
    how_to_like_query = (
        query_lower.startswith("how to")
        or any("step" in header or "how to" in header for header in headers_lower)
    )
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
        if len(page.title_tag) < 12 or title_overlap < 0.15:
            title_confidence = 0.8
        if not generic_site_title:
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
        meta_overlap < 0.26
        or len(page.meta_description) < 40
        or "learn about" in meta_lower
        or "welcome" in meta_lower
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

    if not page.has_author and page.word_count >= 300:
        candidates.append(
            IssueCandidate(
                issue_type="no_author",
                severity="medium",
                reason="The page does not show an author attribution.",
                confidence=0.72 if article_like_page else 0.58,
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
    )
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

    should_expect_direct_answer = not (faq_query and paragraph_overlap >= 0.2)
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

    if how_to_like_query and page.word_count >= 500 and "HowTo" not in schema_types:
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
                confidence=0.8 if page.word_count < 400 else 0.72,
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


def run_episode(task_difficulty: str = "easy") -> float:
    env = GeoAuditEnvironment()
    observation = env.reset(task_difficulty=task_difficulty)
    page = observation.page
    planned_actions = plan_actions(observation)

    print(f"[START] task={task_difficulty} page={page.url}")
    print(f"[START] query={page.target_query}")
    print(f"[PLAN] steps={len(planned_actions)}")

    for action in planned_actions:
        observation = env.step(action)
        print(
            f"[STEP] action={action.action_type} "
            f"issue={action.issue_type or '-'} "
            f"message={observation.message}"
        )
        if observation.done:
            break

    flagged_types = [issue["type"] for issue in observation.flagged_issues]
    print(
        f"[END] reward={observation.reward:.3f} "
        f"flagged={flagged_types} "
        f"done={observation.done}"
    )
    return observation.reward


if __name__ == "__main__":
    rewards: Dict[str, float] = {}
    for difficulty in ("easy", "medium", "hard"):
        print()
        rewards[difficulty] = run_episode(task_difficulty=difficulty)

    print("\n[SUMMARY]")
    for difficulty, reward in rewards.items():
        print(f"{difficulty}: {reward:.3f}")
