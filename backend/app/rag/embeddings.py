from __future__ import annotations

from openai import OpenAI

from app.core.config import get_settings


class OpenAIEmbeddings:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = (
            OpenAI(api_key=settings.openai_api_key, timeout=settings.llm_timeout_seconds)
            if settings.openai_api_key else None
        )
        self.model = settings.embedding_model

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not self.client or not texts:
            return []
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]
