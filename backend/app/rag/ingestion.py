from __future__ import annotations

from pathlib import Path


class DocumentIngestion:
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)

    def load_documents(self) -> list[dict]:
        documents: list[dict] = []
        for path in self.base_dir.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            documents.append({
                "document_id": path.stem,
                "title": path.stem.replace("-", " ").title(),
                "source": str(path),
                "content": text,
                "document_type": "markdown",
            })
        return documents
