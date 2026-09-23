from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.core.config import get_settings
from app.rag.embeddings import OpenAIEmbeddings
from app.rag.vector_store import QdrantStore


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
        self.documents = documents or []

    def search(self, query: str, limit: int | None = None) -> list[RetrievalResult]:
        limit = limit or get_settings().max_chunks
        q = query.lower()
        matches = [
            RetrievalResult(
                document_id=d.get("document_id", "unknown"),
                title=d.get("title", "Untitled"),
                source=d.get("source", "unknown"),
                content=d.get("content", ""),
                score=0.9 if q in d.get("content", "").lower() else 0.3,
                metadata={"document_type": d.get("document_type", "markdown")},
            )
            for d in self.documents
        ]
        return sorted(matches, key=lambda item: item.score, reverse=True)[:limit]


class QdrantRetriever:
    def __init__(self) -> None:
        self.embeddings = OpenAIEmbeddings()
        self.store = QdrantStore()

    def search(self, query: str, limit: int | None = None) -> list[RetrievalResult]:
        vectors = self.embeddings.embed([query])
        if not vectors:
            return []
        return [
            RetrievalResult(
                document_id=str(hit.get("document_id", "unknown")),
                title=str(hit.get("title", "Untitled")),
                source=str(hit.get("source", "unknown")),
                content=str(hit.get("content", "")),
                score=float(hit.get("score", 0.0)),
                metadata={k: v for k, v in hit.items() if k not in {"document_id", "title", "source", "content", "score"}},
            )
            for hit in self.store.search(vectors[0], limit or get_settings().max_chunks)
        ]
