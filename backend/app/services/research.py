from __future__ import annotations

import uuid
from datetime import datetime

from app.graph.workflow import build_graph
from app.graph.state import ResearchState, coerce_state
from app.schemas.research import ResearchRequest, ResearchResponse


def execute_research(request: ResearchRequest) -> ResearchResponse:
    research_id = f"res_{uuid.uuid4().hex[:8]}"
    state = ResearchState(
        research_id=research_id,
        question=request.question,
        status=__import__("app.schemas.research", fromlist=["ResearchStatus"]).ResearchStatus.pending,
        metadata={"created_at": datetime.utcnow().isoformat(), "request": request.model_dump()},
    )

    graph = build_graph()
    result = coerce_state(graph.invoke(state))

    if result.final_report is None:
        return ResearchResponse(
            research_id=research_id,
            status="failed",
            error="Research workflow did not produce a final report.",
            sources=[source for source in result.sources],
        )

    return ResearchResponse(
        research_id=research_id,
        status="completed",
        report=result.final_report,
        sources=result.sources,
    )
