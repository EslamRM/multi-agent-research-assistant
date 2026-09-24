from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

from app.schemas.research import ResearchEvidence, ResearchSummary


@dataclass(frozen=True)
class EvidenceQuality:
    evidence_coverage: float
    source_diversity: float
    citation_coverage: float
    groundedness: float
    overall: float
    warnings: list[str]


def evaluate_evidence(evidence: list[ResearchEvidence], summary: ResearchSummary) -> EvidenceQuality:
    warnings: list[str] = []
    if not evidence:
        return EvidenceQuality(0, 0, 0, 0, 0, ["No evidence was retrieved."])

    source_types = {item.source_type for item in evidence}
    source_diversity = min(1.0, len(source_types) / 2)
    urls = {item.source_url for item in evidence if item.source_url}
    citation_coverage = min(1.0, len(urls) / max(1, len(summary.key_findings)))
    evidence_coverage = min(1.0, len(evidence) / max(1, len(summary.key_findings)))

    supported = 0
    for finding in summary.findings:
        if finding.evidence:
            supported += 1
    groundedness = supported / max(1, len(summary.findings)) if summary.findings else min(1.0, sum(e.confidence for e in evidence) / len(evidence))

    if source_diversity < 1:
        warnings.append("Evidence comes from only one source type.")
    if citation_coverage < 0.8:
        warnings.append("Some key findings may not have directly traceable citations.")
    if groundedness < 0.6:
        warnings.append("Grounding confidence is below the recommended threshold.")

    overall = round(
        0.30 * evidence_coverage
        + 0.20 * source_diversity
        + 0.25 * citation_coverage
        + 0.25 * groundedness,
        3,
    )
    return EvidenceQuality(
        evidence_coverage=round(evidence_coverage, 3),
        source_diversity=round(source_diversity, 3),
        citation_coverage=round(citation_coverage, 3),
        groundedness=round(groundedness, 3),
        overall=overall,
        warnings=warnings,
    )
