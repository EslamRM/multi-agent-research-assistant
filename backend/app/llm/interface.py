from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.research import FinalReport, ResearchPlan, ResearchSummary


class LLMProvider(ABC):
    @abstractmethod
    def plan_research(self, question: str) -> ResearchPlan:
        """Return a structured research plan."""

    @abstractmethod
    def summarize_evidence(self, evidence: list[dict], question: str) -> ResearchSummary:
        """Condense evidence into a structured summary."""

    @abstractmethod
    def generate_report(self, question: str, summary: ResearchSummary, sources: list[dict]) -> FinalReport:
        """Produce the final report from grounded findings."""


class LocalFallbackProvider(LLMProvider):
    def plan_research(self, question: str) -> ResearchPlan:
        lowered = question.lower()
        sub_questions = [
            "What are AI coding assistants and what capabilities do they offer?",
            "What evidence exists on productivity impact in software engineering?",
            "What are the main methodological limitations in current studies?",
            "How do reported gains differ across contexts and team sizes?",
        ]
        if "security" in lowered:
            sub_questions = [
                "What security risks are associated with AI coding assistants?",
                "What evidence exists on secure coding outcomes?",
                "What are the known limitations and controls?",
            ]

        return ResearchPlan(
            question=question,
            sub_questions=sub_questions,
            research_tasks=[
                {"id": "task_1", "description": "Define scope and capabilities", "priority": 1, "depends_on": [], "status": "pending"},
                {"id": "task_2", "description": "Collect evidence on productivity measures", "priority": 2, "depends_on": ["task_1"], "status": "pending"},
                {"id": "task_3", "description": "Review limitations and conflicts", "priority": 3, "depends_on": ["task_2"], "status": "pending"},
            ],
            rationale="The workflow prioritizes definition, evidence collection, and evidence quality checks before final synthesis.",
        )

    def summarize_evidence(self, evidence: list[dict], question: str) -> ResearchSummary:
        claims = [item.get("claim", "Observed productivity effect") for item in evidence]
        return ResearchSummary(
            key_findings=[
                "AI coding assistants often increase task throughput in repetitive development activities.",
                "Reported gains vary widely based on task type, developer experience, and tool quality.",
                "The strongest evidence relates to code generation and boilerplate assistance rather than full-system engineering outcomes.",
            ],
            supporting_evidence=claims[:3],
            contradictions=["Large productivity gains are not universal; outcomes depend heavily on context and implementation quality."],
            limitations=["Evidence quality varies across studies and many reports rely on self-reported measures."],
            missing_information=["Longitudinal industry-wide productivity benchmarks remain limited."],
        )

    def generate_report(self, question: str, summary: ResearchSummary, sources: list[dict]) -> FinalReport:
        source_titles = [source.get("title", "Unknown source") for source in sources]
        return FinalReport(
            title=f"Research report: {question}",
            executive_summary="AI coding assistants are most impactful when used for repetitive, low-context coding tasks, while gains on complex systems engineering remain more mixed and dependent on developer skill and workflow maturity.",
            key_findings=summary.key_findings,
            analysis="The evidence base suggests that productivity effects are real but uneven. Gains are strongest for boilerplate generation, test scaffolding, and code completion, while higher-level planning, debugging, and architectural reasoning still require expert oversight.",
            limitations=summary.limitations,
            sources=source_titles,
            conclusion="AI coding assistants should be treated as force-multipliers for specific tasks rather than substitutes for engineering judgment.",
            confidence=0.72,
        )
