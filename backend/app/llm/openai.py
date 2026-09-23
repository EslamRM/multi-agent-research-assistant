from __future__ import annotations

from openai import OpenAI

from app.core.config import get_settings
from app.llm.interface import LLMProvider, LocalFallbackProvider, parse_json_model
from app.schemas.research import FinalReport, ResearchPlan, ResearchSummary


class OpenAIProvider(LLMProvider):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.fallback = LocalFallbackProvider()
        self.client = OpenAI(api_key=self.settings.openai_api_key, timeout=self.settings.llm_timeout_seconds) if self.settings.openai_api_key else None

    def _json(self, system: str, prompt: str) -> str:
        if not self.client:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        response = self.client.chat.completions.create(
            model=self.settings.openai_model,
            temperature=0.1,
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or "{}"

    def plan_research(self, question: str) -> ResearchPlan:
        try:
            return parse_json_model(
                self._json("Return only valid JSON. Do not invent sources.", f"Create a research plan for: {question}. Include question, sub_questions, research_tasks and rationale."),
                ResearchPlan,
            )
        except Exception:
            return self.fallback.plan_research(question)

    def summarize_evidence(self, evidence: list[dict], question: str) -> ResearchSummary:
        try:
            return parse_json_model(
                self._json("Use only supplied evidence. Preserve uncertainty and conflicts. Return only JSON.", f"Question: {question}\nEvidence: {evidence}\nReturn ResearchSummary."),
                ResearchSummary,
            )
        except Exception:
            return self.fallback.summarize_evidence(evidence, question)

    def generate_report(self, question: str, summary: ResearchSummary, sources: list[dict]) -> FinalReport:
        try:
            return parse_json_model(
                self._json("Use only supplied findings and sources. Never invent citations. Return only JSON.", f"Question: {question}\nSummary: {summary.model_dump_json()}\nSources: {sources}\nReturn FinalReport."),
                FinalReport,
            )
        except Exception:
            return self.fallback.generate_report(question, summary, sources)
