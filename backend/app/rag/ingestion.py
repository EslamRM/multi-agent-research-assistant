from __future__ import annotations

from pathlib import Path

from app.rag.embeddings import OpenAIEmbeddings
from app.rag.vector_store import QdrantStore


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> list[str]:
    clean = " ".join(text.split())
    if not clean:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(clean):
        end = min(len(clean), start + chunk_size)
        chunks.append(clean[start:end])
        if end == len(clean):
            break
        start = end - overlap
    return chunks


class DocumentIngestion:
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)

    def load_documents(self) -> list[dict]:
        documents = []
        if not self.base_dir.exists():
            return documents
        for path in self.base_dir.rglob("*.md"):
            documents.append({
                "document_id": path.stem,
                "title": path.stem.replace("-", " ").title(),
                "source": str(path),
                "content": path.read_text(encoding="utf-8"),
                "document_type": "markdown",
            })
        return documents

    def index_documents(self, documents: list[dict]) -> int:
        embedding = OpenAIEmbeddings()
        store = QdrantStore()
        points = []
        for document in documents:
            chunks = chunk_text(document.get("content", ""))
            vectors = embedding.embed(chunks)
            for index, (chunk, vector) in enumerate(zip(chunks, vectors)):
                points.append((vector, {
                    "document_id": document.get("document_id", "unknown"),
                    "title": document.get("title", "Untitled"),
                    "source": document.get("source", "unknown"),
                    "content": chunk,
                    "document_type": document.get("document_type", "markdown"),
                    "chunk_index": index,
                }))
        if not points:
            return 0
        return store.upsert(points, len(points[0][0]))
