from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class GeoAuditAction:
    """One decision the agent can take during an audit episode."""

    action_type: str
    target: Optional[str] = None
    issue_type: Optional[str] = None
    severity: Optional[str] = None
    details: Optional[str] = None


@dataclass
class PageData:
    """The visible page features the agent can inspect."""

    url: str = ""
    target_query: str = ""
    title_tag: str = ""
    meta_description: str = ""
    h1: str = ""
    first_paragraph: str = ""
    word_count: int = 0
    headers: List[str] = field(default_factory=list)
    schema_types: List[str] = field(default_factory=list)
    has_author: bool = False
    has_date: bool = False
    has_sources: bool = False
    source_count: int = 0


@dataclass
class CheckResults:
    """Stores what the agent has already inspected."""

    title_tag: Optional[Dict] = None
    meta_description: Optional[Dict] = None
    headers: Optional[Dict] = None
    schema: Optional[Dict] = None
    direct_answer: Optional[Dict] = None
    content_structure: Optional[Dict] = None
    word_count: Optional[Dict] = None
    trust_signals: Optional[Dict] = None
    sources: Optional[Dict] = None


@dataclass
class GeoAuditObservation:
    """The observation returned after each reset/step."""

    page: PageData = field(default_factory=PageData)
    checked: CheckResults = field(default_factory=CheckResults)
    flagged_issues: List[Dict] = field(default_factory=list)
    step_count: int = 0
    max_steps: int = 10
    available_actions: List[str] = field(default_factory=list)
    message: str = ""
    done: bool = False
    reward: float = 0.0


@dataclass
class GeoAuditState:
    """Internal episode state the environment uses to grade the agent."""

    episode_id: str = ""
    task_id: str = ""
    task_difficulty: str = ""
    step_count: int = 0
    max_steps: int = 10
    ground_truth_issues: List[Dict] = field(default_factory=list)
    current_page: Dict = field(default_factory=dict)
    checks_performed: List[str] = field(default_factory=list)
    flagged_issues: List[Dict] = field(default_factory=list)
