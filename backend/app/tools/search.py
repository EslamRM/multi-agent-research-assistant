from __future__ import annotations

from app.schemas.research import ResearchSource


def search_sources(query: str, limit: int = 5) -> list[ResearchSource]:
    normalized = query.lower()
    base_sources = [
        ResearchSource(
            id="src_1",
            title="AI coding assistants and software engineering productivity",
            source_type="document",
            url="https://example.com/ai-coding-assistants-productivity",
            author="Research Desk",
            metadata={"topic": "productivity", "query": normalized},
        ),
        ResearchSource(
            id="src_2",
            title="Developer workflows with code generation tools",
            source_type="article",
            url="https://example.com/dev-workflows-code-generation",
            author="Engineering Lab",
            metadata={"topic": "workflow", "query": normalized},
        ),
        ResearchSource(
            id="src_3",
            title="Limitations of AI-assisted development studies",
            source_type="document",
            url="https://example.com/limitations-ai-dev-studies",
            author="Systems Review",
            metadata={"topic": "limitations", "query": normalized},
        ),
    ]
    return base_sources[:limit]
