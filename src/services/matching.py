"""Matching engine for ranking candidates against a role.

Heuristic, transparent scoring. Scores are normalized into [0, 1] per component
and then combined using configurable weights.
"""

from __future__ import annotations

from typing import Iterable, List, Tuple
import os

from ..models.candidate import Candidate
from ..models.role import Role
from ..models.match import MatchResult, ScoreBreakdown


def _norm(value: float) -> float:
    return max(0.0, min(1.0, value))


def _jaccard(a: Iterable[str], b: Iterable[str]) -> float:
    sa = {x.strip().lower() for x in a if x}
    sb = {x.strip().lower() for x in b if x}
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _contains_any(hay: Iterable[str], needles: Iterable[str]) -> bool:
    hs = {x.strip().lower() for x in hay}
    return any((n.strip().lower() in hs) for n in needles)


def _title_signal(candidate: Candidate) -> float:
    titles = [*(candidate.titles or []), candidate.current_title or ""]
    titles_l = [t.lower() for t in titles if t]
    strong = {"cto", "chief technology officer", "head of engineering"}
    mid = {"vp engineering", "vp of engineering", "director of engineering"}
    if any(t in strong for t in titles_l):
        return 1.0
    if any(t in mid for t in titles_l):
        return 0.7
    if any("engineering" in t or "platform" in t for t in titles_l):
        return 0.4
    return 0.0


def score_candidate(
    candidate: Candidate, role: Role, startup_stage: str | None = None
) -> Tuple[float, ScoreBreakdown, List[str]]:
    reasons: List[str] = []

    # Skills: required and nice-to-have
    req_overlap = _jaccard(candidate.skills, role.required_skills)
    nice_overlap = _jaccard(candidate.skills, role.nice_to_have_skills)
    skills_score = _norm(0.8 * req_overlap + 0.2 * nice_overlap)
    if req_overlap >= 0.5:
        reasons.append("Strong skills match on required stack")
    elif req_overlap > 0:
        reasons.append("Partial overlap on required skills")
    else:
        reasons.append("No overlap on required skills")

    # Seniority: heuristic mapping
    desired = role.seniority.value
    seniority_score = 0.0
    titles = [*(candidate.titles or []), candidate.current_title or ""]
    titles_l = [t.lower() for t in titles if t]
    if desired == "cxo" and any(
        "cto" in t or "chief technology" in t for t in titles_l
    ):
        seniority_score = 1.0
        reasons.append("Has held CTO/CXO roles")
    elif desired in {"vp", "head"} and any("vp" in t or "head" in t for t in titles_l):
        seniority_score = 1.0
        reasons.append("Has VP/Head leadership experience")
    elif any("director" in t for t in titles_l):
        seniority_score = 0.6
        reasons.append("Director-level leadership experience")

    # Experience years vs minimum
    exp_score = _norm((candidate.years_experience - role.min_years_experience + 5) / 10)
    if candidate.years_experience >= role.min_years_experience:
        reasons.append("Meets or exceeds years of experience")
    else:
        reasons.append("Below minimum years of experience")

    # Stage preference match
    stage_score = 0.0
    if startup_stage and candidate.stage_preferences:
        stage_score = (
            1.0
            if startup_stage in {s.value for s in candidate.stage_preferences}
            else 0.0
        )
        if stage_score == 1.0:
            reasons.append("Prefers startup stage")

    # Domain match
    domain_score = _jaccard(candidate.domains, [])
    if role and role.required_skills:
        # Use domains list from candidate vs startup domains (handled by caller if needed)
        pass

    # Location / timezone preference
    location_score = 0.0
    if role.location_preference:
        location_score = (
            1.0
            if _contains_any(candidate.locations, [role.location_preference])
            else 0.0
        )
        if location_score == 1.0:
            reasons.append("Location preference satisfied")
    elif role.remote_ok and (
        candidate.remote_preference is None or candidate.remote_preference
    ):
        location_score = 0.8
        reasons.append("Open to remote")

    # Title signal
    title_score = _title_signal(candidate)
    if title_score >= 0.7:
        reasons.append("Previous executive engineering title")

    # Weights (can be tuned via env)
    def w(name: str, default: float) -> float:
        try:
            return float(os.getenv(name, default))
        except Exception:
            return default

    weights = {
        "skills": w("WEIGHT_SKILLS", 0.30),
        "seniority": w("WEIGHT_SENIORITY", 0.15),
        "experience": w("WEIGHT_EXPERIENCE", 0.15),
        "stage": w("WEIGHT_STAGE", 0.15),
        "domain": w("WEIGHT_DOMAIN", 0.10),
        "location": w("WEIGHT_LOCATION", 0.10),
        "title": w("WEIGHT_TITLE", 0.05),
    }

    breakdown = ScoreBreakdown(
        skills=skills_score,
        seniority=seniority_score,
        experience=exp_score,
        stage=stage_score,
        domain=domain_score,
        location=location_score,
        title=title_score,
    )

    overall = (
        breakdown.skills * weights["skills"]
        + breakdown.seniority * weights["seniority"]
        + breakdown.experience * weights["experience"]
        + breakdown.stage * weights["stage"]
        + breakdown.domain * weights["domain"]
        + breakdown.location * weights["location"]
        + breakdown.title * weights["title"]
    )

    return overall, breakdown, reasons


def rank_candidates(
    candidates: List[Candidate],
    role: Role,
    startup_domains: List[str] | None = None,
    startup_stage: str | None = None,
) -> List[MatchResult]:
    # Inject domain match using startup domains if provided
    results: List[MatchResult] = []
    for c in candidates:
        score, breakdown, reasons = score_candidate(c, role, startup_stage)
        # augment domain score if startup domains present
        if startup_domains is not None:
            domain_score = _jaccard(c.domains, startup_domains)
            breakdown.domain = domain_score
            if domain_score >= 0.5:
                reasons.append("Strong domain alignment with startup")
        results.append(
            MatchResult(
                candidate=c, score=round(score, 4), breakdown=breakdown, reasons=reasons
            )
        )

    results.sort(key=lambda r: r.score, reverse=True)
    return results
