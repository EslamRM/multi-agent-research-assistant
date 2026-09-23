from __future__ import annotations

import anthropic

from app.core.config import get_settings
from app.llm.interface import LLMProvider, LocalFallbackProvider, parse_json_model
from app.schemas.research import FinalReport, ResearchPlan, ResearchSummary


class AnthropicProvider(LLMProvider):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.fallback = LocalFallbackProvider()
        self.client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key) if self.settings.anthropic_api_key else None

    def _json(self, system: str, prompt: str) -> str:
        if not self.client:
            raise RuntimeError("ANTHROPIC_API_KEY is not configured")
        response = self.client.messages.create(
            model=self.settings.anthropic_model,
            max_tokens=3000,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if getattr(block, "type", None) == "text")

    def plan_research(self, question: str) -> ResearchPlan:
        try:
            return parse_json_model(self._json("Return only valid JSON. Do not invent sources.", f"Create a research plan for: {question}. Return ResearchPlan."), ResearchPlan)
        except Exception:
            return self.fallback.plan_research(question)

    def summarize_evidence(self, evidence: list[dict], question: str) -> ResearchSummary:
        try:
            return parse_json_model(self._json("Use only supplied evidence. Preserve uncertainty and conflicts. Return only JSON.", f"Question: {question}\nEvidence: {evidence}\nReturn ResearchSummary."), ResearchSummary)
        except Exception:
            return self.fallback.summarize_evidence(evidence, question)

    def generate_report(self, question: str, summary: ResearchSummary, sources: list[dict]) -> FinalReport:
        try:
            return parse_json_model(self._json("Use only supplied findings and sources. Never invent citations. Return only JSON.", f"Question: {question}\nSummary: {summary.model_dump_json()}\nSources: {sources}\nReturn FinalReport."), FinalReport)
        except Exception:
            return self.fallback.generate_report(question, summary, sources)
