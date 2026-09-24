from __future__ import annotations

import logging

from openai import OpenAI

from app.core.config import get_settings
from app.llm.interface import LLMProvider, LocalFallbackProvider, parse_json_model
from app.schemas.research import FinalReport, ResearchPlan, ResearchSummary

logger = logging.getLogger(__name__)


class GroqProvider(LLMProvider):
    """Groq provider using its OpenAI-compatible API."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.fallback = LocalFallbackProvider()
        self.client = (
            OpenAI(
                api_key=self.settings.groq_api_key,
                base_url="https://api.groq.com/openai/v1",
                timeout=self.settings.llm_timeout_seconds,
            )
            if self.settings.groq_api_key
            else None
        )

    def _json(self, system: str, prompt: str) -> str:
        if not self.client:
            raise RuntimeError("GROQ_API_KEY is not configured in the runtime environment")

        response = self.client.chat.completions.create(
            model=self.settings.groq_model,
            temperature=0.1,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content or "{}"

    def plan_research(self, question: str) -> ResearchPlan:
        try:
            return parse_json_model(
                self._json(
                    "You are a research planner. Return only valid JSON matching the ResearchPlan schema. "
                    "Create focused, non-overlapping research questions for the user's question. "
                    "Do not invent sources.",
                    f"Create a research plan for: {question}. "
                    "Include question, sub_questions, research_tasks and rationale.",
                ),
                ResearchPlan,
            )
        except Exception as exc:
            logger.exception("Groq planner failed: model=%s error=%s", self.settings.groq_model, exc)
            return self.fallback.plan_research(question)

    def summarize_evidence(self, evidence: list[dict], question: str) -> ResearchSummary:
        try:
            return parse_json_model(
                self._json(
                    "You are the evidence synthesis agent. Return ONLY JSON matching the ResearchSummary schema. "
                    "Use only supplied evidence. Do not invent facts, sources, citations, or claims. "
                    "Combine duplicate evidence. Produce distinct findings, identify agreement, disagreement, "
                    "uncertainty, and missing information. Each finding must cite supplied evidence IDs.",
                    f"Question: {question}\nEvidence: {evidence}\n"
                    "Return a concise ResearchSummary with distinct findings.",
                ),
                ResearchSummary,
            )
        except Exception as exc:
            logger.exception(
                "Groq summarizer failed: model=%s evidence_count=%s error=%s",
                self.settings.groq_model,
                len(evidence),
                exc,
            )
            return self.fallback.summarize_evidence(evidence, question)

    def generate_report(self, question: str, summary: ResearchSummary, sources: list[dict]) -> FinalReport:
        try:
            return parse_json_model(
                self._json(
                    "You are the final research reporter. Return ONLY JSON matching the FinalReport schema. "
                    "Answer the user's question directly using only the supplied summary and sources. "
                    "Do not repeat source snippets. Synthesize them into coherent findings and analysis. "
                    "Preserve uncertainty and disagreements. Never invent facts, citations, or source titles.",
                    f"Question: {question}\nSummary: {summary.model_dump_json()}\nSources: {sources}\n"
                    "Return a concise, well-structured FinalReport.",
                ),
                FinalReport,
            )
        except Exception as exc:
            logger.exception(
                "Groq reporter failed: model=%s source_count=%s error=%s",
                self.settings.groq_model,
                len(sources),
                exc,
            )
            return self.fallback.generate_report(question, summary, sources)
