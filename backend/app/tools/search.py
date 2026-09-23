from __future__ import annotations

from typing import Any

import httpx

from app.core.config import get_settings
from app.schemas.research import ResearchSource


def _tavily_search(query: str, limit: int) -> list[ResearchSource]:
    settings = get_settings()
    if not settings.tavily_api_key:
        return []
    response = httpx.post(
        "https://api.tavily.com/search",
        json={"api_key": settings.tavily_api_key, "query": query, "search_depth": "advanced", "max_results": limit},
        timeout=settings.search_timeout_seconds,
    )
    response.raise_for_status()
    payload: dict[str, Any] = response.json()
    return [
        ResearchSource(
            id=f"web_{i}",
            title=item.get("title") or item.get("url") or f"Search result {i}",
            source_type="web",
            url=item.get("url"),
            metadata={"query": query, "provider": "tavily", "snippet": item.get("content", ""), "score": item.get("score")},
        )
        for i, item in enumerate(payload.get("results", []), 1)
    ]


def _wikipedia_search(query: str, limit: int) -> list[ResearchSource]:
    settings = get_settings()
    response = httpx.get(
        "https://en.wikipedia.org/w/api.php",
        params={"action":"query","list":"search","format":"json","srsearch":query,"srlimit":limit,"utf8":1},
        timeout=settings.search_timeout_seconds,
    )
    response.raise_for_status()
    results = response.json().get("query", {}).get("search", [])
    return [
        ResearchSource(
            id=f"wiki_{item.get('pageid', i)}",
            title=item.get("title", "Wikipedia result"),
            source_type="web",
            url=f"https://en.wikipedia.org/?curid={item.get('pageid')}" if item.get("pageid") else None,
            metadata={"query": query, "provider": "wikipedia", "snippet": item.get("snippet", "")},
        )
        for i, item in enumerate(results, 1)
    ]


def search_sources(query: str, limit: int = 5) -> list[ResearchSource]:
    try:
        sources = _tavily_search(query, limit)
        if sources:
            return sources
    except (httpx.HTTPError, ValueError):
        pass
    try:
        return _wikipedia_search(query, limit)
    except (httpx.HTTPError, ValueError):
        return []
