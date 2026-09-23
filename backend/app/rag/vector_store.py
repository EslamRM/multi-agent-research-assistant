from __future__ import annotations

import hashlib
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.core.config import get_settings


class QdrantStore:
    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key or None,
            timeout=settings.search_timeout_seconds,
        )

    def ensure_collection(self, vector_size: int) -> None:
        names = {item.name for item in self.client.get_collections().collections}
        if self.settings.qdrant_collection not in names:
            self.client.create_collection(
                collection_name=self.settings.qdrant_collection,
                vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
            )

    def upsert(self, points: list[tuple[list[float], dict[str, Any]]], vector_size: int) -> int:
        if not points:
            return 0
        self.ensure_collection(vector_size)
        self.client.upsert(
            collection_name=self.settings.qdrant_collection,
            points=[
                models.PointStruct(
                    id=hashlib.sha256(str(payload).encode()).hexdigest()[:32],
                    vector=vector,
                    payload=payload,
                )
                for vector, payload in points
            ],
        )
        return len(points)

    def search(self, vector: list[float], limit: int) -> list[dict[str, Any]]:
        return [
            {"score": hit.score, **(hit.payload or {})}
            for hit in self.client.search(
                collection_name=self.settings.qdrant_collection,
                query_vector=vector,
                limit=limit,
            )
        ]
