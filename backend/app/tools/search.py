from __future__ import annotations

import re
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
        json={
            "api_key": settings.tavily_api_key,
            "query": query,
            "search_depth": "advanced",
            "max_results": limit,
        },
        timeout=settings.search_timeout_seconds,
    )
    response.raise_for_status()
    payload: dict[str, Any] = response.json()
    return [
        ResearchSource(
            id=f"web_tavily_{i}",
            title=item.get("title") or item.get("url") or f"Search result {i}",
            source_type="web",
            url=item.get("url"),
            metadata={
                "query": query,
                "provider": "tavily",
                "snippet": item.get("content", ""),
                "score": item.get("score"),
            },
        )
        for i, item in enumerate(payload.get("results", []), 1)
        if item.get("url")
    ]


def _wikipedia_search(query: str, limit: int) -> list[ResearchSource]:
    settings = get_settings()
    response = httpx.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "list": "search",
            "format": "json",
            "srsearch": query,
            "srlimit": limit,
            "utf8": 1,
        },
        headers={"User-Agent": "MultiAgentResearchAssistant/1.0"},
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
            metadata={
                "query": query,
                "provider": "wikipedia",
                "snippet": re.sub(r"<[^>]+>", "", item.get("snippet", "")),
                "score": 0.55,
            },
        )
        for i, item in enumerate(results, 1)
        if item.get("pageid")
    ]


def _duckduckgo_search(query: str, limit: int) -> list[ResearchSource]:
    settings = get_settings()
    response = httpx.get(
        "https://html.duckduckgo.com/html/",
        params={"q": query},
        headers={"User-Agent": "Mozilla/5.0 MultiAgentResearchAssistant/1.0"},
        timeout=settings.search_timeout_seconds,
    )
    response.raise_for_status()
    html = response.text

    blocks = re.findall(
        r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    snippets = re.findall(
        r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    results: list[ResearchSource] = []
    for i, (url, title_html) in enumerate(blocks[:limit], 1):
        title = re.sub(r"<[^>]+>", "", title_html).strip()
        snippet = re.sub(r"<[^>]+>", "", snippets[i - 1]).strip() if i <= len(snippets) else ""
        if url and title:
            results.append(
                ResearchSource(
                    id=f"web_ddg_{i}",
                    title=title,
                    source_type="web",
                    url=url,
                    metadata={
                        "query": query,
                        "provider": "duckduckgo",
                        "snippet": snippet,
                        "score": 0.5,
                    },
                )
            )
    return results


def search_sources(query: str, limit: int = 5) -> list[ResearchSource]:
    """Aggregate providers instead of accepting the first weak provider result."""
    providers = (_tavily_search, _duckduckgo_search, _wikipedia_search)
    merged: dict[str, ResearchSource] = {}

    for provider in providers:
        try:
            provider_limit = max(2, min(limit, 5))
            for source in provider(query, provider_limit):
                key = source.url or source.id
                merged.setdefault(key, source)
                if len(merged) >= limit:
                    break
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            continue
        if len(merged) >= limit:
            break

    return list(merged.values())[:limit]
