from app.schemas.research import ResearchEvidence, ResearchFinding
from app.services.grounding import assess_finding


def test_claim_with_matching_evidence_is_supported():
    evidence = ResearchEvidence(
        id="e1",
        claim="coding productivity",
        evidence="AI coding assistants improve coding productivity for repetitive tasks",
        source_id="s1",
        source_title="Study",
        source_type="web",
        confidence=0.9,
    )
    finding = ResearchFinding(id="f1", claim="AI coding assistants improve coding productivity", evidence=[evidence], confidence=0.8)

    result = assess_finding(finding, [evidence])

    assert result.supported
    assert result.citation_ids == ["s1"]


def test_claim_without_related_evidence_is_unsupported():
    evidence = ResearchEvidence(
        id="e1",
        claim="weather",
        evidence="The weather is sunny today",
        source_id="s1",
        source_title="Weather",
        source_type="web",
        confidence=0.9,
    )
    finding = ResearchFinding(id="f1", claim="Database indexing reduces query latency", evidence=[], confidence=0.8)

    result = assess_finding(finding, [evidence])

    assert not result.supported
    assert result.warning
