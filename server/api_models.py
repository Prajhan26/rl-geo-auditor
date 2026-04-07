from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ResetRequest(BaseModel):
    """Request body for starting a new episode."""

    task_difficulty: Literal["easy", "medium", "hard"] = "easy"


class StepRequest(BaseModel):
    """Request body for applying one environment action."""

    action_type: str = Field(
        ...,
        examples=["check_meta_description", "flag_issue", "submit_report"],
    )
    target: Optional[str] = None
    issue_type: Optional[str] = None
    severity: Optional[str] = None
    details: Optional[str] = None


class HealthResponse(BaseModel):
    status: Literal["healthy"]


class MetadataResponse(BaseModel):
    name: str
    description: str
    version: str
    available_actions: List[str]
    issue_types: List[str]


class PageDataResponse(BaseModel):
    url: str
    target_query: str
    title_tag: str
    meta_description: str
    h1: str
    first_paragraph: str
    word_count: int
    headers: List[str]
    schema_types: List[str]
    has_author: bool
    has_date: bool
    has_sources: bool
    source_count: int


class CheckResultsResponse(BaseModel):
    title_tag: Optional[Dict[str, Any]] = None
    meta_description: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, Any]] = None
    schema_result: Optional[Dict[str, Any]] = Field(default=None, alias="schema")
    direct_answer: Optional[Dict[str, Any]] = None
    content_structure: Optional[Dict[str, Any]] = None
    word_count: Optional[Dict[str, Any]] = None
    trust_signals: Optional[Dict[str, Any]] = None
    sources: Optional[Dict[str, Any]] = None


class FlaggedIssueResponse(BaseModel):
    type: str
    severity: str
    details: str


class ObservationResponse(BaseModel):
    page: PageDataResponse
    checked: CheckResultsResponse
    flagged_issues: List[FlaggedIssueResponse]
    step_count: int
    max_steps: int
    available_actions: List[str]
    message: str
    done: bool
    reward: float
