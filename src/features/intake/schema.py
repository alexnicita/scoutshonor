"""Schema and helpers for capturing an intake packet before sourcing.

Key dependencies:
    - pydantic for validation
    - src.models.common.Seniority enum to keep levels consistent with roles
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, List, Optional

from pydantic import BaseModel, Field, ValidationError, field_validator

from ...models.common import Seniority


class HiringManager(BaseModel):
    name: str
    email: Optional[str] = None
    department: Optional[str] = None


class ScorecardCompetency(BaseModel):
    name: str
    weight: float = Field(
        1.0,
        ge=0.0,
        description="Relative weight for this competency when scoring candidates.",
    )
    signals: List[str] = Field(
        default_factory=list,
        description="Observable signals this competency should surface.",
    )
    knockout_questions: List[str] = Field(
        default_factory=list,
        description="Quick questions to rule out obvious mismatches.",
    )

    @field_validator("weight")
    def _normalize_weight(cls, value: float) -> float:
        return round(value, 3)


class IntakeForm(BaseModel):
    role_id: str
    role_title: str
    seniority: Seniority
    startup_name: str
    mission: str
    goals: List[str] = Field(default_factory=list)
    must_have_skills: List[str] = Field(default_factory=list)
    nice_to_have_skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    remote_ok: bool = True
    compensation_range: Optional[str] = None
    success_metrics: List[str] = Field(default_factory=list)
    interview_panel: List[str] = Field(default_factory=list)
    hiring_manager: HiringManager
    scorecard: List[ScorecardCompetency] = Field(default_factory=list)

    @field_validator(
        "goals",
        "must_have_skills",
        "nice_to_have_skills",
        "responsibilities",
        mode="before",
    )
    def _strip_blanks(cls, values: Iterable[str]) -> List[str]:
        if values is None:
            return []
        if isinstance(values, str):
            values = [values]
        cleaned = [v.strip() for v in values if v and v.strip()]
        return cleaned

    def summary(self) -> str:
        """Human-readable summary used by the CLI."""
        top_skills = ", ".join(self.must_have_skills[:3]) or "n/a"
        goals = "; ".join(self.goals[:2]) or "n/a"
        return (
            f"{self.role_title} ({self.seniority.value}) at {self.startup_name} | "
            f"top skills: {top_skills} | goals: {goals}"
        )

    def to_json_file(self, path: Path | str) -> Path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(self.model_dump(), indent=2, sort_keys=True), encoding="utf-8"
        )
        return destination

    @classmethod
    def from_json_file(cls, path: Path | str) -> "IntakeForm":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(**data)


def load_intake(path: Path | str) -> IntakeForm:
    """Load an intake JSON file and validate it."""
    return IntakeForm.from_json_file(path)


def save_intake(form: IntakeForm, path: Path | str) -> Path:
    """Persist an intake form as JSON."""
    return form.to_json_file(path)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and persist an intake form.")
    parser.add_argument(
        "--input",
        default="examples/intake_sample.json",
        help="Path to an intake JSON payload.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional path to write the validated payload (defaults to input).",
    )
    parser.add_argument(
        "--print-summary",
        action="store_true",
        help="Print a one-line summary after validation.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    output_path = args.output or args.input
    try:
        form = load_intake(args.input)
    except (OSError, ValidationError, json.JSONDecodeError) as exc:
        parser.error(f"Failed to load intake file: {exc}")
        return 1

    save_intake(form, output_path)
    if args.print_summary:
        print(form.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
