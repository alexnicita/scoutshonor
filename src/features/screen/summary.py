"""Summarize parsed resumes and flag screening risks."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from .parser import ResumeProfile


class RiskSummary(BaseModel):
    summary: str
    risks: List[str] = Field(default_factory=list)


def summarize_candidate(profile: ResumeProfile, required_skills: List[str]) -> RiskSummary:
    """Build a condensed summary and risk list from parsed data."""

    missing_skills = {
        skill
        for skill in (required_skills or [])
        if skill.lower() not in {s.lower() for s in profile.skills}
    }
    risks: List[str] = []
    if missing_skills:
        risks.append(f"Missing required skills: {', '.join(sorted(missing_skills))}")
    if not profile.email:
        risks.append("Contact email missing")
    if not profile.phone:
        risks.append("Contact phone missing")

    summary_bits: List[str] = []
    if profile.years_experience:
        summary_bits.append(f"{profile.years_experience} years experience")
    if profile.skills:
        summary_bits.append(f"key skills: {', '.join(profile.skills[:5])}")
    if profile.summary:
        summary_bits.append(profile.summary)

    summary_text = "; ".join(summary_bits) or "No summary available"
    return RiskSummary(summary=summary_text, risks=risks)
