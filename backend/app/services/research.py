from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.graph.state import ResearchState, coerce_state
from app.graph.workflow import build_graph
from app.schemas.research import ResearchRequest, ResearchResponse, ResearchStatus


def execute_research(request: ResearchRequest) -> ResearchResponse:
    research_id = f"res_{uuid.uuid4().hex[:8]}"
    state = ResearchState(
        research_id=research_id,
        question=request.question,
        status=ResearchStatus.pending,
        metadata={
            "created_at": datetime.now(timezone.utc).isoformat(),
            "request": request.model_dump(),
            "max_sources": request.max_sources,
            "research_mode": request.research_mode,
        },
    )

    result = coerce_state(build_graph().invoke(state))

    if result.final_report is None:
        return ResearchResponse(
            research_id=research_id,
            status="failed",
            error=result.errors[-1].message if result.errors else "Research workflow did not produce a final report.",
            sources=result.sources,
            metadata={"errors": [error.model_dump() for error in result.errors], **result.metadata},
        )

    return ResearchResponse(
        research_id=research_id,
        status="completed",
        report=result.final_report,
        sources=result.sources,
        metadata=result.metadata,
    )
