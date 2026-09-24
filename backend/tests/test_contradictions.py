from app.schemas.research import ResearchEvidence
from app.services.contradictions import detect_conflicts


def test_detects_opposing_evidence():
    evidence = [
        ResearchEvidence(id="a", claim="productivity", evidence="The tool increased developer productivity significantly", source_id="s1", source_title="Study A", source_type="web", confidence=0.8),
        ResearchEvidence(id="b", claim="productivity", evidence="The tool did not increase developer productivity significantly", source_id="s2", source_title="Study B", source_type="web", confidence=0.8),
    ]

    conflicts = detect_conflicts(evidence)

    assert conflicts
    assert conflicts[0].evidence_a == "a"
    assert conflicts[0].evidence_b == "b"


def test_does_not_compare_same_source():
    evidence = [
        ResearchEvidence(id="a", claim="x", evidence="The tool increased productivity", source_id="same", source_title="Study", source_type="web", confidence=0.8),
        ResearchEvidence(id="b", claim="x", evidence="The tool did not increase productivity", source_id="same", source_title="Study", source_type="web", confidence=0.8),
    ]

    assert detect_conflicts(evidence) == []
