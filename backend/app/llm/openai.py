from __future__ import annotations

from app.core.config import get_settings
from app.llm.interface import LLMProvider, LocalFallbackProvider


class OpenAIProvider(LLMProvider):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.fallback = LocalFallbackProvider()

    def plan_research(self, question: str):
        if not self.settings.openai_api_key:
            return self.fallback.plan_research(question)
        return self.fallback.plan_research(question)

    def summarize_evidence(self, evidence: list[dict], question: str):
        if not self.settings.openai_api_key:
            return self.fallback.summarize_evidence(evidence, question)
        return self.fallback.summarize_evidence(evidence, question)

    def generate_report(self, question: str, summary, sources: list[dict]):
        if not self.settings.openai_api_key:
            return self.fallback.generate_report(question, summary, sources)
        return self.fallback.generate_report(question, summary, sources)
