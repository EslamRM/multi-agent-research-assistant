from __future__ import annotations

from openai import OpenAI
import logging

from app.core.config import get_settings
from app.llm.interface import LLMProvider, LocalFallbackProvider, parse_json_model
from app.schemas.research import FinalReport, ResearchPlan, ResearchSummary

logger = logging.getLogger(__name__)


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
        except Exception as exc:
            logger.exception("OpenAI planner failed: model=%s error=%s", self.settings.openai_model, exc)
            return self.fallback.plan_research(question)

    def summarize_evidence(self, evidence: list[dict], question: str) -> ResearchSummary:
        try:
            return parse_json_model(
                self._json(
                    "You are the evidence synthesis agent. Return ONLY JSON matching the ResearchSummary schema. "
                    "Use only the supplied evidence. Do not invent facts, sources, citations, or claims. "
                    "Combine duplicate evidence into one finding. Identify agreement, disagreement, uncertainty, "
                    "and missing information. Each finding must cite one or more supplied evidence IDs.",
                    f"Question: {question}\nEvidence: {evidence}\nReturn a concise ResearchSummary with distinct findings.",
                ),
                ResearchSummary,
            )
        except Exception as exc:
            logger.exception(
                "OpenAI summarizer failed: model=%s evidence_count=%s error=%s",
                self.settings.openai_model,
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
                    "Do not repeat source snippets. Synthesize them into a coherent analysis. "
                    "Preserve uncertainty and disagreements. Never invent facts, citations, or source titles.",
                    f"Question: {question}\nSummary: {summary.model_dump_json()}\nSources: {sources}\nReturn a concise, well-structured FinalReport.",
                ),
                FinalReport,
            )
        except Exception as exc:
            logger.exception(
                "OpenAI reporter failed: model=%s source_count=%s error=%s",
                self.settings.openai_model,
                len(sources),
                exc,
            )
            return self.fallback.generate_report(question, summary, sources)
