"""Dry-run ATS sync for pushing screening notes."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel

from .summary import RiskSummary


class AtsSyncResult(BaseModel):
    candidate_id: str
    note: str
    dry_run: bool = True
    delivered: bool = False


class AtsSync:
    """Compose ATS notes; keep delivery dry-run for offline testing."""

    def __init__(self) -> None:
        self.pushed: List[AtsSyncResult] = []

    def push_note(self, candidate_id: str, risk_summary: RiskSummary) -> AtsSyncResult:
        note_lines = [
            f"Summary: {risk_summary.summary}",
            f"Risks: {', '.join(risk_summary.risks) if risk_summary.risks else 'None'}",
        ]
        payload = AtsSyncResult(
            candidate_id=candidate_id,
            note="\n".join(note_lines),
            dry_run=True,
            delivered=False,
        )
        self.pushed.append(payload)
        return payload
