"""Lightweight resume parser for offline screening."""

from __future__ import annotations

import re
from typing import List, Optional, Set

from pydantic import BaseModel, Field


class ResumeProfile(BaseModel):
    """Structured profile data extracted from a resume."""

    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    years_experience: Optional[int] = None
    summary: str = ""


class ResumeParser:
    """Parse plaintext resumes using heuristics and a small skill library."""

    def __init__(self, skill_library: Optional[Set[str]] = None) -> None:
        default_skills = {
            "python",
            "fastapi",
            "aws",
            "gcp",
            "kubernetes",
            "sql",
            "postgresql",
            "redis",
            "docker",
        }
        self.skill_library = {s.lower() for s in (skill_library or default_skills)}

    def parse(self, text: str) -> ResumeProfile:
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        full_name = lines[0] if lines else "Unknown"
        normalized = text.lower()

        email = _extract_email(normalized)
        phone = _extract_phone(normalized)
        years = _extract_years_of_experience(normalized)
        skills = sorted({s for s in self.skill_library if s in normalized})
        summary = " ".join(lines[1:3]) if len(lines) > 1 else ""

        return ResumeProfile(
            full_name=full_name,
            email=email,
            phone=phone,
            skills=skills,
            years_experience=years,
            summary=summary,
        )


def _extract_email(text: str) -> Optional[str]:
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+", text)
    return match.group(0) if match else None


def _extract_phone(text: str) -> Optional[str]:
    match = re.search(r"(?:\+?\d{1,2}[-\s]?)?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}", text)
    return match.group(0) if match else None


def _extract_years_of_experience(text: str) -> Optional[int]:
    match = re.search(r"(\d{1,2})\+?\s+years", text)
    return int(match.group(1)) if match else None
