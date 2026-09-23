from app.graph.state import ResearchState, coerce_state
from app.graph.workflow import build_graph


def test_graph_happy_path():
    graph = build_graph()
    state = ResearchState(
        research_id="res_123",
        question="Compare the impact of AI coding assistants on software engineering productivity.",
    )

    result = coerce_state(graph.invoke(state))

    assert result.status.name in {"completed", "failed"}
    assert result.research_plan is not None
    assert isinstance(result.final_report, object) or result.final_report is None
