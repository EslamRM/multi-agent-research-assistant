from __future__ import annotations

import re
from dataclasses import dataclass

from app.schemas.research import ResearchEvidence


@dataclass(frozen=True)
class ConflictAssessment:
    evidence_a: str
    evidence_b: str
    score: float
    reason: str


_NEGATION = re.compile(r"\b(no|not|never|without|cannot|can't|fails?|failed|decrease|decreased|lower|worse|negative|unlikely)\b", re.I)


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-Z0-9]{4,}", text.lower())}


def _polarity(text: str) -> int:
    return -1 if len(_NEGATION.findall(text)) % 2 else 1


def detect_conflicts(evidence: list[ResearchEvidence], min_overlap: float = 0.22) -> list[ConflictAssessment]:
    conflicts: list[ConflictAssessment] = []
    for index, left in enumerate(evidence):
        for right in evidence[index + 1:]:
            if left.source_id == right.source_id:
                continue
            left_tokens = _tokens(left.evidence)
            right_tokens = _tokens(right.evidence)
            overlap = len(left_tokens & right_tokens) / max(1, min(len(left_tokens), len(right_tokens)))
            if overlap >= min_overlap and _polarity(left.evidence) != _polarity(right.evidence):
                conflicts.append(
                    ConflictAssessment(
                        evidence_a=left.id,
                        evidence_b=right.id,
                        score=round(min(1.0, overlap), 3),
                        reason="Sources discuss overlapping terms with opposing polarity; treat the claim as contested until verified.",
                    )
                )
    return conflicts
