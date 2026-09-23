from app.graph.state import ResearchState, coerce_state
from app.graph import workflow
from app.schemas.research import ResearchSource


def test_graph_happy_path(monkeypatch):
    monkeypatch.setattr(
        workflow,
        "search_sources",
        lambda query, limit=5: [
            ResearchSource(
                id="test_source",
                title="Test source",
                source_type="test",
                url="https://example.com/test",
                metadata={"snippet": "Evidence for the research question.", "score": 0.9},
            )
        ],
    )

    result = coerce_state(
        workflow.build_graph().invoke(
            ResearchState(research_id="res_123", question="What is a useful research question?")
        )
    )

    assert result.research_plan is not None
    assert result.sources
    assert result.evidence
    assert result.summary is not None
    assert result.final_report is not None
    assert result.status.name == "completed"


def test_graph_fails_without_evidence(monkeypatch):
    monkeypatch.setattr(workflow, "search_sources", lambda query, limit=5: [])

    result = coerce_state(
        workflow.build_graph().invoke(
            ResearchState(research_id="res_456", question="A valid research question")
        )
    )

    assert result.status.name == "failed"
    assert result.final_report is None
    assert result.errors
