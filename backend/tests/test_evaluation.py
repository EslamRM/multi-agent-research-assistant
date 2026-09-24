from app.schemas.research import ResearchEvidence, ResearchFinding, ResearchSummary
from app.services.evaluation import evaluate_evidence


def test_quality_score_rewards_grounded_diverse_evidence():
    evidence = [
        ResearchEvidence(id="1", claim="c1", evidence="e1", source_id="s1", source_title="Web", source_url="https://example.com", source_type="web", confidence=0.9),
        ResearchEvidence(id="2", claim="c2", evidence="e2", source_id="s2", source_title="Document", source_url="https://docs.example.com", source_type="document", confidence=0.9),
    ]
    summary = ResearchSummary(
        key_findings=["c1", "c2"],
        findings=[
            ResearchFinding(id="f1", claim="c1", evidence=[evidence[0]], confidence=0.9),
            ResearchFinding(id="f2", claim="c2", evidence=[evidence[1]], confidence=0.9),
        ],
    )

    quality = evaluate_evidence(evidence, summary)

    assert quality.overall >= 0.8
    assert quality.groundedness == 1.0
    assert not quality.warnings


def test_quality_score_warns_when_citations_are_missing():
    evidence = [
        ResearchEvidence(id="1", claim="c1", evidence="e1", source_id="s1", source_title="Source", source_type="web", confidence=0.4),
    ]
    summary = ResearchSummary(key_findings=["c1", "c2"])

    quality = evaluate_evidence(evidence, summary)

    assert quality.citation_coverage < 0.8
    assert quality.warnings
