import json
import random
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

from .grader import calculate_reward
from .models import (
    CheckResults,
    GeoAuditAction,
    GeoAuditObservation,
    GeoAuditState,
    PageData,
)


class GeoAuditEnvironment:
    """
    A small RL-style environment for GEO page auditing.

    reset() starts a new page audit.
    step() applies one action such as checking metadata or flagging an issue.
    """

    AVAILABLE_ACTIONS = [
        "check_title_tag",
        "check_meta_description",
        "check_headers",
        "check_schema",
        "check_direct_answer",
        "check_content_structure",
        "check_word_count",
        "check_trust_signals",
        "check_sources",
        "flag_issue",
        "mark_positive",
        "submit_report",
    ]

    ISSUE_TYPES = [
        "missing_title_tag",
        "weak_title_tag",
        "missing_meta_description",
        "weak_meta_description",
        "no_direct_answer",
        "buried_answer",
        "missing_faq_schema",
        "missing_howto_schema",
        "missing_article_schema",
        "no_headers",
        "poor_header_structure",
        "thin_content",
        "no_author",
        "no_date",
        "no_sources",
    ]

    POSITIVE_TYPES = [
        "clear_direct_answer",
        "strong_title_tag",
        "strong_meta_description",
        "good_heading_structure",
        "has_faq_schema",
        "has_howto_schema",
        "has_article_schema",
        "has_author",
        "has_date",
        "has_sources",
        "comprehensive_content",
    ]

    def __init__(self) -> None:
        self._state = GeoAuditState()
        self._data = self._load_data()

    def _load_data(self) -> Dict[str, List[Dict]]:
        data_dir = Path(__file__).parent.parent / "data"
        return {
            "easy": self._load_json(data_dir / "task1_easy.json"),
            "medium": self._load_json(data_dir / "task2_medium.json"),
            "hard": self._load_json(data_dir / "task3_hard.json"),
        }

    def _load_json(self, path: Path) -> List[Dict]:
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def reset(self, task_difficulty: str = "easy") -> GeoAuditObservation:
        pages = self._data.get(task_difficulty, [])
        page = random.choice(pages) if pages else self._get_dummy_page()

        self._state = GeoAuditState(
            episode_id=str(uuid.uuid4()),
            task_id=page.get("page_id", "unknown"),
            task_difficulty=task_difficulty,
            step_count=0,
            max_steps=10,
            ground_truth_issues=page.get("issues", []),
            ground_truth_positives=page.get("positives", []),
            current_page=page,
            checks_performed=[],
            flagged_issues=[],
            marked_positives=[],
        )

        return self._build_observation(
            message=(
                "Audit started. Inspect the page, flag issues, then submit the report. "
                f"Target query: '{page.get('target_query', '')}'"
            )
        )

    def step(self, action: GeoAuditAction) -> GeoAuditObservation:
        self._state.step_count += 1

        if self._state.step_count > self._state.max_steps:
            return self._finalize("Max steps reached. Auto-submitting report.")

        if action.action_type.startswith("check_"):
            return self._handle_check(action)
        if action.action_type == "flag_issue":
            return self._handle_flag(action)
        if action.action_type == "mark_positive":
            return self._handle_positive(action)
        if action.action_type == "submit_report":
            return self._finalize("Report submitted.")

        return self._build_observation(message=f"Unknown action: {action.action_type}")

    def _handle_check(self, action: GeoAuditAction) -> GeoAuditObservation:
        if action.action_type in self._state.checks_performed:
            return self._build_observation(
                message=f"Already checked: {action.action_type}"
            )

        self._state.checks_performed.append(action.action_type)
        result = self._analyze(action.action_type.replace("check_", ""))
        return self._build_observation(message=result)

    def _handle_flag(self, action: GeoAuditAction) -> GeoAuditObservation:
        if not action.issue_type:
            return self._build_observation(
                message="flag_issue requires an issue_type."
            )

        if action.issue_type not in self.ISSUE_TYPES:
            return self._build_observation(
                message=f"Unknown issue type: {action.issue_type}"
            )

        issue = {
            "type": action.issue_type,
            "severity": action.severity or "medium",
            "details": action.details or "",
        }

        existing_types = {item["type"] for item in self._state.flagged_issues}
        if issue["type"] not in existing_types:
            self._state.flagged_issues.append(issue)

        return self._build_observation(
            message=f"Flagged issue: {issue['type']} ({issue['severity']})"
        )

    def _handle_positive(self, action: GeoAuditAction) -> GeoAuditObservation:
        if not action.positive_type:
            return self._build_observation(
                message="mark_positive requires a positive_type."
            )

        if action.positive_type not in self.POSITIVE_TYPES:
            return self._build_observation(
                message=f"Unknown positive type: {action.positive_type}"
            )

        positive = {
            "type": action.positive_type,
            "details": action.details or "",
        }

        existing_types = {item["type"] for item in self._state.marked_positives}
        if positive["type"] not in existing_types:
            self._state.marked_positives.append(positive)

        return self._build_observation(
            message=f"Marked positive: {positive['type']}"
        )

    def _analyze(self, check_type: str) -> str:
        page = self._state.current_page

        if check_type == "title_tag":
            title = page.get("title_tag", "")
            if not title:
                return "Title check: no title tag found."
            return f"Title check: '{title}' ({len(title)} chars)."

        if check_type == "meta_description":
            meta = page.get("meta_description", "")
            if not meta:
                return "Meta description check: missing."
            return f"Meta description check: '{meta[:100]}' ({len(meta)} chars)."

        if check_type == "headers":
            headers = page.get("headers", [])
            h1 = page.get("h1", "")
            return f"Header check: H1='{h1}', section headers={headers}."

        if check_type == "schema":
            schemas = page.get("schema_types", [])
            if not schemas:
                return "Schema check: no schema markup found."
            return f"Schema check: found {schemas}."

        if check_type == "direct_answer":
            paragraph = page.get("first_paragraph", "")
            query = page.get("target_query", "")
            return (
                "Direct answer check: "
                f"query='{query}', opening paragraph='{paragraph[:140]}'."
            )

        if check_type == "content_structure":
            return (
                "Content structure check: "
                f"{len(page.get('headers', []))} headers, "
                f"{page.get('word_count', 0)} words."
            )

        if check_type == "word_count":
            count = page.get("word_count", 0)
            if count < 300:
                return f"Word count check: thin content ({count} words)."
            if count < 500:
                return f"Word count check: light content ({count} words)."
            return f"Word count check: healthy length ({count} words)."

        if check_type == "trust_signals":
            return (
                "Trust signal check: "
                f"author={page.get('has_author', False)}, "
                f"date={page.get('has_date', False)}."
            )

        if check_type == "sources":
            return (
                "Source check: "
                f"has_sources={page.get('has_sources', False)}, "
                f"source_count={page.get('source_count', 0)}."
            )

        return f"Unknown check type: {check_type}"

    def _finalize(self, message: str) -> GeoAuditObservation:
        reward = calculate_reward(
            flagged=self._state.flagged_issues,
            ground_truth=self._state.ground_truth_issues,
            marked_positives=self._state.marked_positives,
            ground_truth_positives=self._state.ground_truth_positives,
        )
        return self._build_observation(message=message, done=True, reward=reward)

    def _build_observation(
        self,
        message: str = "",
        done: bool = False,
        reward: float = 0.0,
    ) -> GeoAuditObservation:
        page = self._state.current_page
        return GeoAuditObservation(
            page=PageData(
                url=page.get("url", ""),
                target_query=page.get("target_query", ""),
                title_tag=page.get("title_tag", ""),
                meta_description=page.get("meta_description", ""),
                h1=page.get("h1", ""),
                first_paragraph=page.get("first_paragraph", ""),
                word_count=page.get("word_count", 0),
                headers=page.get("headers", []),
                schema_types=page.get("schema_types", []),
                has_author=page.get("has_author", False),
                has_date=page.get("has_date", False),
                has_sources=page.get("has_sources", False),
                source_count=page.get("source_count", 0),
            ),
            checked=self._build_check_results(),
            flagged_issues=self._state.flagged_issues,
            marked_positives=self._state.marked_positives,
            step_count=self._state.step_count,
            max_steps=self._state.max_steps,
            available_actions=self.AVAILABLE_ACTIONS,
            message=message,
            done=done,
            reward=reward,
        )

    def observation_dict(self, observation: GeoAuditObservation) -> Dict:
        """Convert nested dataclasses into plain JSON-friendly structures."""
        return asdict(observation)

    def _build_check_results(self) -> CheckResults:
        page = self._state.current_page
        results = CheckResults()

        for check in self._state.checks_performed:
            check_type = check.replace("check_", "")

            if check_type == "title_tag":
                results.title_tag = {
                    "present": bool(page.get("title_tag")),
                    "value": page.get("title_tag", ""),
                    "length": len(page.get("title_tag", "")),
                }
            elif check_type == "meta_description":
                results.meta_description = {
                    "present": bool(page.get("meta_description")),
                    "value": page.get("meta_description", ""),
                    "length": len(page.get("meta_description", "")),
                }
            elif check_type == "headers":
                results.headers = {
                    "h1": page.get("h1", ""),
                    "headers": page.get("headers", []),
                }
            elif check_type == "schema":
                results.schema = {"schema_types": page.get("schema_types", [])}
            elif check_type == "direct_answer":
                results.direct_answer = {
                    "first_paragraph": page.get("first_paragraph", "")
                }
            elif check_type == "content_structure":
                results.content_structure = {
                    "header_count": len(page.get("headers", [])),
                    "word_count": page.get("word_count", 0),
                }
            elif check_type == "word_count":
                results.word_count = {"word_count": page.get("word_count", 0)}
            elif check_type == "trust_signals":
                results.trust_signals = {
                    "has_author": page.get("has_author", False),
                    "has_date": page.get("has_date", False),
                }
            elif check_type == "sources":
                results.sources = {
                    "has_sources": page.get("has_sources", False),
                    "source_count": page.get("source_count", 0),
                }

        return results

    def _get_dummy_page(self) -> Dict:
        return {
            "page_id": "dummy_001",
            "url": "https://example.com/how-to-stake-ethereum",
            "target_query": "how to stake ethereum",
            "title_tag": "Ethereum Staking Basics",
            "meta_description": "",
            "h1": "Ethereum Staking Guide",
            "first_paragraph": (
                "Welcome to our blockchain blog. We love crypto and share updates "
                "for curious readers exploring new technologies."
            ),
            "word_count": 280,
            "headers": ["H2: About", "H2: Contact"],
            "schema_types": [],
            "has_author": False,
            "has_date": False,
            "has_sources": False,
            "source_count": 0,
            "issues": [
                {"type": "missing_meta_description", "severity": "critical"},
                {"type": "no_direct_answer", "severity": "critical"},
                {"type": "thin_content", "severity": "medium"},
            ],
            "positives": [],
        }

    @property
    def state(self) -> GeoAuditState:
        return self._state

    def current_observation(self) -> GeoAuditObservation:
        if not self._state.current_page:
            return self._build_observation(
                message="No active episode. Call reset() to start an audit."
            )
        return self._build_observation(message="Current episode state.")
