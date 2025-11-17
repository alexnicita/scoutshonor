"""CSV importer with dedupe and simple enrichment hooks."""

from __future__ import annotations

import csv
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional


@dataclass
class ImportedCandidate:
    full_name: str
    current_title: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    location: Optional[str] = None
    raw: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def _split_skills(value: str | None) -> List[str]:
    if not value:
        return []
    separators = [";", "|", ","]
    for sep in separators:
        if sep in value:
            return [v.strip() for v in value.split(sep) if v.strip()]
    return [value.strip()] if value.strip() else []


def _fingerprint(candidate: ImportedCandidate) -> str:
    if candidate.email:
        return candidate.email.lower()
    name = (candidate.full_name or "").strip().lower()
    company = (candidate.company or "").strip().lower()
    return f"{name}|{company}"


Enricher = Callable[[ImportedCandidate], ImportedCandidate]


def import_candidates_from_csv(
    path: Path | str,
    dedupe: bool = True,
    enrichers: Optional[Iterable[Enricher]] = None,
) -> List[ImportedCandidate]:
    """Import candidates from CSV, dedupe, and run optional enrichers.

    Expected headers (case-insensitive):
        full_name, current_title, company, email, skills, location
    Unrecognized columns are preserved in the `raw` dict for later use.
    """
    candidates: Dict[str, ImportedCandidate] = {}
    enrichers = list(enrichers or [])

    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            normalized_row = {k.lower().strip(): v for k, v in row.items()}
            candidate = ImportedCandidate(
                full_name=normalized_row.get("full_name", "").strip(),
                current_title=normalized_row.get("current_title")
                or normalized_row.get("title"),
                company=normalized_row.get("company"),
                email=normalized_row.get("email"),
                skills=_split_skills(normalized_row.get("skills")),
                location=normalized_row.get("location"),
                raw=normalized_row,
            )
            for enricher in enrichers:
                candidate = enricher(candidate)
            if dedupe:
                candidates.setdefault(_fingerprint(candidate), candidate)
            else:
                candidates[f"{_fingerprint(candidate)}|{len(candidates)}"] = candidate
    return list(candidates.values())


def basic_enricher(candidate: ImportedCandidate) -> ImportedCandidate:
    """Fill in lightweight derived fields for ranking context."""
    raw = candidate.raw or {}
    note_fields = ["summary", "notes", "bio"]
    snippets = [raw.get(field) for field in note_fields if raw.get(field)]
    if snippets and "skills" in raw and not candidate.skills:
        candidate.skills = _split_skills(raw["skills"])
    if snippets:
        candidate.raw["evidence"] = snippets
    return candidate


__all__ = ["import_candidates_from_csv", "ImportedCandidate", "basic_enricher"]
