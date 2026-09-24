from __future__ import annotations

import re
from dataclasses import dataclass

from app.schemas.research import ResearchEvidence, ResearchFinding


@dataclass(frozen=True)
class ClaimAssessment:
    finding_id: str
    supported: bool
    support_score: float
    contradiction_count: int
    citation_ids: list[str]
    warning: str | None = None


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-Z0-9]{4,}", text.lower())}


def assess_finding(finding: ResearchFinding, evidence: list[ResearchEvidence]) -> ClaimAssessment:
    claim_tokens = _tokens(finding.claim)
    related = []
    for item in evidence:
        overlap = len(claim_tokens & _tokens(item.evidence)) / max(1, len(claim_tokens))
        if item.source_id in {ev.source_id for ev in finding.evidence} or overlap >= 0.15:
            related.append((item, overlap))

    if not related:
        return ClaimAssessment(finding.id, False, 0.0, len(finding.contradictions), [], "No directly related evidence was found.")

    best = max(score for _, score in related)
    confidence = sum(item.confidence for item, _ in related) / len(related)
    support_score = min(1.0, 0.6 * best + 0.4 * confidence)
    supported = support_score >= 0.35
    warning = None if supported else "Evidence relevance is weak for this claim."
    return ClaimAssessment(
        finding.id,
        supported,
        round(support_score, 3),
        len(finding.contradictions),
        [item.source_id for item, _ in related],
        warning,
    )


def assess_findings(findings: list[ResearchFinding], evidence: list[ResearchEvidence]) -> list[ClaimAssessment]:
    return [assess_finding(finding, evidence) for finding in findings]
