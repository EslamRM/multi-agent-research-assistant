from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.research import FinalReport, ResearchPlan, ResearchSummary


class LLMProvider(ABC):
    @abstractmethod
    def plan_research(self, question: str) -> ResearchPlan:
        pass

    @abstractmethod
    def summarize_evidence(self, evidence: list[dict], question: str) -> ResearchSummary:
        pass

    @abstractmethod
    def generate_report(self, question: str, summary: ResearchSummary, sources: list[dict]) -> FinalReport:
        pass


def _build_fallback_plan(question: str) -> ResearchPlan:
    q = question.strip()
    lowered = q.lower()

    if any(word in lowered for word in ("latest", "newest", "current", "models", "model", "compare")):
        sub_questions = [
            f"Which current AI models are relevant to: {q}?",
            f"What are the documented capabilities and major differences of the models relevant to: {q}?",
            f"What are the latest official model versions, availability, and context or modality characteristics?",
            f"What limitations, pricing, or usage constraints are documented for those models?",
        ]
    elif "security" in lowered:
        sub_questions = [
            f"What are the main security considerations for: {q}?",
            f"What evidence and documented risks exist for: {q}?",
            f"What mitigations or controls are recommended for: {q}?",
        ]
    else:
        sub_questions = [
            f"What is the scope and current state of: {q}?",
            f"What evidence supports the main claims about: {q}?",
            f"What limitations, disagreements, or uncertainty exist around: {q}?",
            f"What are the practical implications of the evidence for: {q}?",
        ]

    tasks = [
        {"id": f"task_{i}", "description": item, "priority": i, "depends_on": [f"task_{i-1}"] if i > 1 else [], "status": "pending"}
        for i, item in enumerate(sub_questions, 1)
    ]
    return ResearchPlan(
        question=q,
        sub_questions=sub_questions,
        research_tasks=tasks,
        rationale="The fallback planner creates question-specific research tasks so retrieval can proceed even when an LLM provider is unavailable.",
    )


def _fallback_summary(evidence: list[dict], question: str) -> ResearchSummary:
    findings = []
    seen: set[tuple[str, str]] = set()
    for i, item in enumerate(evidence[:10], 1):
        text = str(item.get("evidence") or "").strip()
        if not text:
            continue
        from app.schemas.research import ResearchEvidence, ResearchFinding
        ev = ResearchEvidence.model_validate(item)
        key = (ev.source_id, ev.evidence[:250])
        if key in seen:
            continue
        seen.add(key)
        findings.append(
            ResearchFinding(
                id=f"finding_{i}",
                claim=ev.claim,
                evidence=[ev],
                confidence=ev.confidence,
            )
        )
    return ResearchSummary(
        key_findings=[item.claim for item in findings[:5]],
        supporting_evidence=[item.evidence[0].evidence[:900] for item in findings[:5]],
        contradictions=[],
        limitations=["Fallback synthesis was used; the LLM provider was unavailable or returned invalid structured output."],
        missing_information=[],
        findings=findings,
    )


def _fallback_report(question: str, summary: ResearchSummary, sources: list[dict]) -> FinalReport:
    source_titles = [str(source.get("title", "Unknown source")) for source in sources]
    return FinalReport(
        title=f"Research report: {question}",
        executive_summary=(
            f"Research retrieved {len(sources)} source(s) relevant to the question. "
            "The report below is grounded in the retrieved evidence rather than a prewritten answer."
        ),
        key_findings=summary.key_findings,
        analysis="\n\n".join(summary.supporting_evidence) or "No additional analysis was produced.",
        limitations=summary.limitations,
        sources=source_titles,
        conclusion="The available evidence should be interpreted together with the listed sources and stated limitations.",
        confidence=min((float(item.get("confidence", 0.5)) for item in sources), default=0.5),
        citations=[],
    )


class LocalFallbackProvider(LLMProvider):
    def plan_research(self, question: str) -> ResearchPlan:
        return _build_fallback_plan(question)

    def summarize_evidence(self, evidence: list[dict], question: str) -> ResearchSummary:
        return _fallback_summary(evidence, question)

    def generate_report(self, question: str, summary: ResearchSummary, sources: list[dict]) -> FinalReport:
        return _fallback_report(question, summary, sources)


def parse_json_model(raw: str, model_type):
    import json
    return model_type.model_validate(json.loads(raw))
