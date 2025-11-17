"""Ranking wrapper that scores imported candidates against a scorecard."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

from ..intake.schema import ScorecardCompetency
from .importer import ImportedCandidate


def _normalize_weights(scorecard: Sequence[ScorecardCompetency]) -> List[float]:
    total = sum(item.weight for item in scorecard) or 1.0
    return [item.weight / total for item in scorecard]


def _collect_text(candidate: ImportedCandidate) -> str:
    fields = [
        candidate.full_name or "",
        candidate.current_title or "",
        candidate.company or "",
    ]
    if candidate.skills:
        fields.append(" ".join(candidate.skills))
    raw_values = candidate.raw.values() if candidate.raw else []
    return " ".join(fields + list(raw_values)).lower()


def _score_competency(
    text_blob: str, competency: ScorecardCompetency
) -> Tuple[float, List[str]]:
    hits: List[str] = []
    for signal in competency.signals:
        if signal.lower() in text_blob:
            hits.append(signal)
    coverage = len(hits) / len(competency.signals) if competency.signals else 0.0
    return coverage, hits


@dataclass
class RankedCandidate:
    candidate: ImportedCandidate
    score: float
    evidence: Dict[str, List[str]]


def rank_candidates(
    candidates: Iterable[ImportedCandidate], scorecard: Sequence[ScorecardCompetency]
) -> List[RankedCandidate]:
    """Return ordered candidates with evidence for each scorecard competency."""
    weights = _normalize_weights(scorecard)
    ranked: List[RankedCandidate] = []

    for candidate in candidates:
        text_blob = _collect_text(candidate)
        evidence: Dict[str, List[str]] = {}
        total_score = 0.0
        for weight, competency in zip(weights, scorecard):
            comp_score, hits = _score_competency(text_blob, competency)
            evidence[competency.name] = hits
            total_score += comp_score * weight
        ranked.append(
            RankedCandidate(candidate=candidate, score=round(total_score, 4), evidence=evidence)
        )

    ranked.sort(key=lambda item: item.score, reverse=True)
    return ranked


__all__ = ["rank_candidates", "RankedCandidate"]
