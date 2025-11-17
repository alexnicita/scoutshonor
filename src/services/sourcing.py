"""Sourcing utilities: generate boolean search strings for external platforms.

Purpose:
  Help recruiters quickly craft boolean/X-Ray searches for LinkedIn, Google,
  and GitHub using a Role definition. This is deterministic and template-based.
"""

from __future__ import annotations

from typing import Iterable, List

from ..models.role import Role


def _clean(words: Iterable[str]) -> List[str]:
    return [w.strip() for w in words if w and w.strip()]


def _title_synonyms(title: str) -> List[str]:
    t = (title or "").lower()
    out: List[str] = []
    # Generic engineering leadership synonyms
    if "vp" in t or "vice president" in t:
        out += [
            "VP Engineering",
            "VP of Engineering",
            "Vice President Engineering",
            "Head of Engineering",
        ]
    if "head" in t:
        out += ["Head of Engineering", "Director of Engineering", "VP Engineering"]
    if "director" in t:
        out += ["Director of Engineering", "Head of Engineering"]
    if "cto" in t or "chief" in t:
        out += ["CTO", "Chief Technology Officer", "VP Engineering"]
    # Default catch-all around engineering leadership
    out += ["Engineering Leader", "Eng Leadership", "Platform Engineering"]
    # Deduplicate preserving order
    seen = set()
    dedup = []
    for s in out:
        if s.lower() not in seen:
            seen.add(s.lower())
            dedup.append(s)
    return dedup


def build_boolean_strings(
    role: Role,
    locations: List[str] | None = None,
    extras: List[str] | None = None,
) -> dict:
    """Generate boolean search strings across platforms.

    - LinkedIn keyword query
    - Google X-Ray for LinkedIn profiles
    - GitHub search by topics/bio
    """
    title_terms = _title_synonyms(role.title)
    req = _clean(role.required_skills)
    nice = _clean(role.nice_to_have_skills)
    locs = _clean(locations or [])
    extra = _clean(extras or [])

    # Build OR groups
    def or_group(terms: List[str]) -> str:
        if not terms:
            return ""
        if len(terms) == 1:
            return f'"{terms[0]}"'
        return "(" + " OR ".join(f'"{t}"' for t in terms) + ")"

    titles_or = or_group(title_terms)
    req_or = or_group(req)
    nice_or = or_group(nice)
    extra_or = or_group(extra)
    loc_or = or_group(locs)

    # LinkedIn Keyword query (to paste into LinkedIn search bar)
    li_parts = [p for p in [titles_or, req_or, nice_or, extra_or, loc_or] if p]
    linkedin = " AND ".join(li_parts)

    # Google X-Ray for LinkedIn
    xr_parts = [
        "site:linkedin.com/in",
        "-jobs -job",
        titles_or or "",
        req_or or "",
        nice_or or "",
        extra_or or "",
    ]
    google_xray = " ".join(p for p in xr_parts if p)
    if loc_or:
        google_xray += f" \"{loc_or.strip('()')}\""

    # GitHub search (topics/bio, coarse)
    gh_terms = [*(req[:3] or []), *(nice[:2] or [])]
    gh_query = " ".join(f"topic:{t}" for t in gh_terms)
    if not gh_query:
        gh_query = "engineering leadership"

    return {
        "linkedin": linkedin,
        "google_xray": google_xray,
        "github": gh_query,
    }
