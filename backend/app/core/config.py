from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    app_name: str = "multi-agent-research-assistant"
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai").lower()
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    groq_model: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    anthropic_api_key: str | None = os.getenv("ANTHROPIC_API_KEY")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    tavily_api_key: str | None = os.getenv("TAVILY_API_KEY")
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key: str | None = os.getenv("QDRANT_API_KEY")
    qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "research_documents")
    max_research_iterations: int = _int_env("MAX_RESEARCH_ITERATIONS", 2)
    max_sources: int = _int_env("MAX_SOURCES", 5)
    max_chunks: int = _int_env("MAX_CHUNKS", 20)
    search_timeout_seconds: int = _int_env("SEARCH_TIMEOUT_SECONDS", 8)
    llm_timeout_seconds: int = _int_env("LLM_TIMEOUT_SECONDS", 30)
    max_question_length: int = _int_env("MAX_QUESTION_LENGTH", 1000)
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


@lru_cache
def get_settings() -> Settings:
    return Settings()
