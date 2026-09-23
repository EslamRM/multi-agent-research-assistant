from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.core.config import get_settings


@dataclass
class RetrievalResult:
    document_id: str
    title: str
    source: str
    content: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


class SimpleRetriever:
    def __init__(self, documents: list[dict] | None = None):
        self.settings = get_settings()
        self.documents = documents or []

    def search(self, query: str, limit: int | None = None) -> list[RetrievalResult]:
        limit = limit or self.settings.max_chunks
        query_lower = query.lower()
        matches: list[RetrievalResult] = []
        for document in self.documents:
            text = document.get("content", "")
            if query_lower in text.lower():
                score = 0.9
            else:
                score = 0.3
            matches.append(
                RetrievalResult(
                    document_id=document.get("document_id", "unknown"),
                    title=document.get("title", "Untitled"),
                    source=document.get("source", "unknown"),
                    content=text,
                    score=score,
                    metadata={"document_type": document.get("document_type", "markdown")},
                )
            )
        return matches[:limit]
