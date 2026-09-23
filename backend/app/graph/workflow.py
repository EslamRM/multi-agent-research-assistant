from __future__ import annotations

import logging

from langgraph.graph import END, StateGraph

from app.core.config import get_settings
from app.graph.state import ResearchState
from app.llm.factory import get_llm_provider
from app.schemas.research import ResearchEvidence, ResearchStatus
from app.tools.search import search_sources

logger = logging.getLogger(__name__)


def planner_node(state: ResearchState) -> ResearchState:
    plan = get_llm_provider().plan_research(state.question)
    state.research_plan = plan
    state.status = ResearchStatus.planning
    state.metadata["plan"] = plan.model_dump()
    return state


def researcher_node(state: ResearchState) -> ResearchState:
    state.status = ResearchStatus.researching
    if not state.research_plan:
        state.add_error("researcher", "Planner did not produce a plan.", code="missing_plan")
        state.mark_failed()
        return state

    state.tasks = [task.model_dump() for task in state.research_plan.research_tasks]
    queries = [task["description"] for task in state.tasks[:get_settings().max_research_iterations + 1]] or [state.question]
    source_map = {}

    for query in queries:
        try:
            for source in search_sources(query, limit=state.metadata.get("max_sources", get_settings().max_sources)):
                source_map[source.url or source.id] = source
        except Exception as exc:
            logger.warning("research search failed: %s", exc)
            state.add_error("researcher", "Search provider failed.", retryable=True, code="search_failed")

    state.sources = list(source_map.values())[:state.metadata.get("max_sources", get_settings().max_sources)]
    state.evidence = [
        ResearchEvidence(
            id=f"ev_{i}",
            claim=f"Evidence relevant to: {state.question}",
            evidence=str(source.metadata.get("snippet") or source.title)[:4000],
            source_id=source.id,
            source_title=source.title,
            source_url=source.url,
            source_type=source.source_type,
            confidence=max(0.0, min(1.0, float(source.metadata.get("score") or 0.6))),
            notes=f"Retrieved from {source.metadata.get('provider', source.source_type)}.",
        )
        for i, source in enumerate(state.sources, 1)
    ]
    state.completed_tasks = [task["id"] for task in state.tasks] if state.sources else []
    state.metadata["source_count"] = len(state.sources)
    state.metadata["evidence_count"] = len(state.evidence)
    return state


def quality_check_node(state: ResearchState) -> ResearchState:
    enough = bool(state.sources and state.evidence)
    state.metadata["enough_evidence"] = enough
    state.should_continue = enough
    if not enough:
        state.add_error("quality_check", "No usable evidence was retrieved.", retryable=True, code="insufficient_evidence")
        state.mark_failed()
    return state


def summarizer_node(state: ResearchState) -> ResearchState:
    state.summary = get_llm_provider().summarize_evidence(
        [item.model_dump() for item in state.evidence], state.question
    )
    state.status = ResearchStatus.summarizing
    return state


def reporter_node(state: ResearchState) -> ResearchState:
    state.status = ResearchStatus.reporting
    state.final_report = get_llm_provider().generate_report(
        state.question,
        state.summary,
        [source.model_dump() for source in state.sources],
    )
    state.status = ResearchStatus.completed
    return state


def build_graph():
    workflow = StateGraph(ResearchState)
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("quality_check", quality_check_node)
    workflow.add_node("summarizer", summarizer_node)
    workflow.add_node("reporter", reporter_node)
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "quality_check")

    def decide_next(state: ResearchState) -> str:
        return "summarizer" if state.should_continue else END

    workflow.add_conditional_edges("quality_check", decide_next, {"summarizer": "summarizer", END: END})
    workflow.add_edge("summarizer", "reporter")
    workflow.add_edge("reporter", END)
    return workflow.compile()
