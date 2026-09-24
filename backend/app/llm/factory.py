from __future__ import annotations

from app.core.config import get_settings
from app.llm.anthropic import AnthropicProvider
from app.llm.interface import LLMProvider, LocalFallbackProvider
from app.llm.openai import OpenAIProvider
from app.llm.groq import GroqProvider


def get_llm_provider(provider_name: str | None = None) -> LLMProvider:
    provider = (provider_name or get_settings().llm_provider).lower()
    if provider == "anthropic":
        return AnthropicProvider()
    if provider == "openai":
        return OpenAIProvider()
    if provider == "groq":
        return GroqProvider()
    return LocalFallbackProvider()
