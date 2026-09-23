from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.schemas.research import (
    AgentError,
    FinalReport,
    ResearchEvidence,
    ResearchPlan,
    ResearchSource,
    ResearchStatus,
    ResearchSummary,
)


def coerce_state(value: ResearchState | dict[str, Any] | None) -> ResearchState:
    if value is None:
        return ResearchState()
    if isinstance(value, ResearchState):
        return value
    data = dict(value)
    return ResearchState(**data)


@dataclass
class ResearchState:
    research_id: str = ""
    question: str = ""
    status: ResearchStatus = ResearchStatus.pending
    research_plan: ResearchPlan | None = None
    tasks: list[dict[str, Any]] = field(default_factory=list)
    completed_tasks: list[str] = field(default_factory=list)
    sources: list[ResearchSource] = field(default_factory=list)
    evidence: list[ResearchEvidence] = field(default_factory=list)
    findings: list[dict[str, Any]] = field(default_factory=list)
    summary: ResearchSummary | None = None
    final_report: FinalReport | None = None
    errors: list[AgentError] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    should_continue: bool = True
    iteration_count: int = 0

    def add_error(self, step: str, message: str, retryable: bool = False, code: str = "unknown_error") -> None:
        self.errors.append(AgentError(step=step, message=message, retryable=retryable, code=code))

    def mark_completed(self) -> None:
        self.status = ResearchStatus.completed
        self.should_continue = False

    def mark_failed(self) -> None:
        self.status = ResearchStatus.failed
        self.should_continue = False
