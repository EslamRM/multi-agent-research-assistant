from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class ResearchSource(BaseModel):
    id: str
    title: str
    source_type: str = Field(..., description="web, document, internal, article")
    url: str | None = None
    author: str | None = None
    published_at: datetime | None = None
    section: str | None = None
    page: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ResearchTask(BaseModel):
    id: str
    description: str
    priority: int = Field(default=1)
    depends_on: list[str] = Field(default_factory=list)
    status: Literal["pending", "completed", "failed"] = "pending"


class ResearchPlan(BaseModel):
    question: str
    sub_questions: list[str] = Field(default_factory=list)
    research_tasks: list[ResearchTask] = Field(default_factory=list)
    rationale: str = ""


class ResearchEvidence(BaseModel):
    id: str
    claim: str
    evidence: str
    source_id: str
    source_title: str
    source_url: str | None = None
    source_type: str
    confidence: float = Field(ge=0.0, le=1.0)
    notes: str = ""


class ResearchFinding(BaseModel):
    id: str
    claim: str
    evidence: list[ResearchEvidence]
    contradictions: list[str] = Field(default_factory=list)
    uncertainty: str = ""
    confidence: float = Field(ge=0.0, le=1.0)


class ResearchSummary(BaseModel):
    key_findings: list[str] = Field(default_factory=list)
    supporting_evidence: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)


class FinalReport(BaseModel):
    title: str
    executive_summary: str
    key_findings: list[str] = Field(default_factory=list)
    analysis: str
    limitations: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    conclusion: str
    confidence: float = Field(ge=0.0, le=1.0)


class ResearchRequest(BaseModel):
    question: str = Field(..., min_length=3)
    max_sources: int = Field(default=5, ge=1, le=20)
    research_mode: Literal["deep", "standard"] = "standard"


class ResearchResponse(BaseModel):
    research_id: str
    status: Literal["completed", "failed", "in_progress"]
    report: FinalReport | None = None
    sources: list[ResearchSource] = Field(default_factory=list)
    error: str | None = None


class AgentError(BaseModel):
    step: str
    message: str
    retryable: bool = False
    code: str = "unknown_error"


class WorkflowMetadata(BaseModel):
    request_id: str
    created_at: datetime
    updated_at: datetime
    model: str | None = None
    provider: str | None = None
    latency_ms: int | None = None
    token_usage: dict[str, int] = Field(default_factory=dict)
    source_count: int = 0
    status: str = "pending"


class ResearchStatus(str, Enum):
    pending = "pending"
    planning = "planning"
    researching = "researching"
    summarizing = "summarizing"
    reporting = "reporting"
    completed = "completed"
    failed = "failed"
