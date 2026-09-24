from __future__ import annotations

import logging

from langgraph.graph import END, StateGraph

from app.core.config import get_settings
from app.graph.state import ResearchState
from app.llm.factory import get_llm_provider
from app.rag.retriever import QdrantRetriever
from app.schemas.research import ResearchEvidence, ResearchSource, ResearchStatus
from app.services.evaluation import evaluate_evidence
from app.services.grounding import assess_findings
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
    source_map: dict[str, ResearchSource] = {}

    for query in queries:
        try:
            for source in search_sources(query, limit=state.metadata.get("max_sources", get_settings().max_sources)):
                source_map[source.url or source.id] = source
        except Exception:
            state.add_error("researcher", "Web search provider failed.", retryable=True, code="search_failed")

    try:
        for item in QdrantRetriever().search(state.question, limit=get_settings().max_chunks):
            key = f"document:{item.document_id}:{item.metadata.get('chunk_index', 0)}"
            source_map[key] = ResearchSource(
                id=f"doc_{item.document_id}_{item.metadata.get('chunk_index', 0)}",
                title=item.title,
                source_type="document",
                url=item.source if item.source.startswith("http") else None,
                metadata={"snippet": item.content, "score": item.score, "document_id": item.document_id, "chunk_index": item.metadata.get("chunk_index")},
            )
    except Exception:
        logger.info("Qdrant retrieval unavailable; continuing with web research.")

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
    state.metadata.update({
        "source_count": len(state.sources),
        "evidence_count": len(state.evidence),
        "retrieval_types": sorted({source.source_type for source in state.sources}),
    })
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
    state.summary = get_llm_provider().summarize_evidence([item.model_dump() for item in state.evidence], state.question)
    state.status = ResearchStatus.summarizing
    return state


def reporter_node(state: ResearchState) -> ResearchState:
    state.status = ResearchStatus.reporting
    state.final_report = get_llm_provider().generate_report(
        state.question, state.summary, [source.model_dump() for source in state.sources]
    )
    quality = evaluate_evidence(state.evidence, state.summary)
    assessments = assess_findings(state.summary.findings, state.evidence)
    unsupported = [item for item in assessments if not item.supported]
    state.metadata["claim_grounding"] = [item.__dict__ for item in assessments]
    if unsupported:
        quality_warnings = list(quality.warnings)
        quality_warnings.append(f"{len(unsupported)} finding(s) have weak direct evidence support.")
        quality = type(quality)(quality.evidence_coverage, quality.source_diversity, quality.citation_coverage, quality.groundedness, quality.overall * max(0.0, 1.0 - 0.15 * len(unsupported)), quality_warnings)
    state.metadata["quality"] = quality.__dict__
    state.final_report.confidence = min(state.final_report.confidence, quality.overall)
    state.final_report.limitations = list(dict.fromkeys(state.final_report.limitations + quality.warnings))
    state.status = ResearchStatus.completed
    return state


def build_graph():
    workflow = StateGraph(ResearchState)
    for name, node in {"planner": planner_node, "researcher": researcher_node, "quality_check": quality_check_node, "summarizer": summarizer_node, "reporter": reporter_node}.items():
        workflow.add_node(name, node)
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "quality_check")

    def decide_next(state: ResearchState) -> str:
        return "summarizer" if state.should_continue else END

    workflow.add_conditional_edges("quality_check", decide_next, {"summarizer": "summarizer", END: END})
    workflow.add_edge("summarizer", "reporter")
    workflow.add_edge("reporter", END)
    return workflow.compile()
