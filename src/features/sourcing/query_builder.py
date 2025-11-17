"""Search query builder for sourcing pipelines.

Uses deterministic templates to generate boolean/X-Ray queries across platforms.
"""

from __future__ import annotations

from typing import Dict, Iterable, List

from pydantic import BaseModel, Field


class SearchProfile(BaseModel):
    title: str
    must_have_skills: List[str] = Field(default_factory=list)
    nice_to_have_skills: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)
    industries: List[str] = Field(default_factory=list)
    exclude_terms: List[str] = Field(default_factory=list)


def _clean(values: Iterable[str]) -> List[str]:
    return [v.strip() for v in values if v and v.strip()]


def _or_clause(values: List[str]) -> str:
    if not values:
        return ""
    if len(values) == 1:
        return f"\"{values[0]}\""
    return "(" + " OR ".join(f"\"{v}\"" for v in values) + ")"


def build_queries(profile: SearchProfile) -> Dict[str, str]:
    """Create platform-specific boolean/X-Ray queries."""
    title = profile.title.strip()
    skills = _clean([*profile.must_have_skills, *profile.nice_to_have_skills])
    locations = _clean(profile.locations)
    industries = _clean(profile.industries)
    excludes = _clean(profile.exclude_terms)

    skills_clause = _or_clause(skills)
    loc_clause = _or_clause(locations)
    industry_clause = _or_clause(industries)
    exclude_clause = " ".join(f"-{term}" for term in excludes) if excludes else ""

    linkedin_parts = [f"\"{title}\""]
    if skills_clause:
        linkedin_parts.append(skills_clause)
    if loc_clause:
        linkedin_parts.append(loc_clause)
    linkedin_query = " AND ".join(linkedin_parts)

    google_parts = [
        "site:linkedin.com/in",
        f"\"{title}\"",
        skills_clause,
        industry_clause,
        exclude_clause,
    ]
    google_query = " ".join([part for part in google_parts if part]).strip()

    wellfound_parts = [
        "site:wellfound.com/u",
        f"\"{title}\"",
        skills_clause,
        industry_clause,
        loc_clause,
    ]
    wellfound_query = " ".join([part for part in wellfound_parts if part]).strip()

    github_parts = [f"\"{title}\""] + [f"language:{skill}" for skill in skills[:3]]
    github_query = " ".join(github_parts)

    return {
        "linkedin": linkedin_query,
        "google_xray": google_query,
        "wellfound": wellfound_query,
        "github": github_query,
    }


__all__ = ["SearchProfile", "build_queries"]
