"""Generate hiring manager brief, candidate-facing JD, and scorecard from intake.

Key dependencies:
    - IntakeForm schema for validated intake payloads
    - Pure string formatting; no external providers to keep outputs deterministic
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from .schema import IntakeForm, ScorecardCompetency, load_intake


def _output_dir(role_id: str, base_dir: Path | str | None = None) -> Path:
    root = Path(base_dir or "assets/outputs")
    path = root / role_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def render_hiring_manager_brief(form: IntakeForm) -> str:
    required = ", ".join(form.must_have_skills) or "Not provided"
    nice = ", ".join(form.nice_to_have_skills) or "Not provided"
    goals = "\n".join(f"- {goal}" for goal in form.goals) or "- Not provided"
    responsibilities = (
        "\n".join(f"- {item}" for item in form.responsibilities) or "- Not provided"
    )
    metrics = "\n".join(f"- {metric}" for metric in form.success_metrics) or "- TBD"
    panel = ", ".join(form.interview_panel) or "TBD"
    location = form.location or "Flexible/Remote"
    compensation = form.compensation_range or "Discuss with recruiting"
    return f"""# Hiring Manager Brief — {form.role_title}

## Context
- Startup: {form.startup_name}
- Mission: {form.mission}
- Goals:
{goals}

## Role
- Title: {form.role_title} ({form.seniority.value})
- Location: {location}
- Remote OK: {"Yes" if form.remote_ok else "No"}
- Compensation: {compensation}
- Interview panel: {panel}

## Requirements
- Must have: {required}
- Nice to have: {nice}
- Responsibilities:
{responsibilities}

## Success metrics (first 6 months)
{metrics}
"""


def render_candidate_jd(form: IntakeForm) -> str:
    required = ", ".join(form.must_have_skills) or "Curiosity and willingness to learn"
    nice = (
        "\n".join(f"- {skill}" for skill in form.nice_to_have_skills)
        if form.nice_to_have_skills
        else "- Bonus experience welcome, not required"
    )
    responsibilities = (
        "\n".join(f"- {item}" for item in form.responsibilities)
        if form.responsibilities
        else "- Help shape this role collaboratively"
    )
    perks = [
        "Early ownership on a critical platform track",
        "Tight partnership with product and go-to-market",
        "Pragmatic engineering culture that values clarity",
    ]
    perks_block = "\n".join(f"- {perk}" for perk in perks)
    return f"""# {form.role_title} — Candidate Overview

### Why {form.startup_name}
- {form.mission}
- You will {form.goals[0] if form.goals else "directly impact customers from day one"}

### What you'll do
{responsibilities}

### What will set you up for success
- Core skills: {required}
{nice}

### What you'll love
{perks_block}
"""


def build_scorecard_payload(form: IntakeForm) -> Dict[str, List[Dict[str, object]]]:
    """Normalize scorecard entries into a serializable payload."""
    entries: List[ScorecardCompetency] = form.scorecard
    total_weight = sum(item.weight for item in entries) or 1.0
    normalized = []
    for item in entries:
        normalized.append(
            {
                "competency": item.name,
                "weight": round(item.weight / total_weight, 3),
                "signals": item.signals,
                "knockout_questions": item.knockout_questions,
            }
        )
    return {"role_id": form.role_id, "scorecard": normalized}


def generate_artifacts(
    form: IntakeForm, output_base_dir: Path | str | None = None
) -> Dict[str, Path]:
    """Write HM brief, candidate JD, and scorecard files to assets."""
    target_dir = _output_dir(form.role_id, output_base_dir)
    hm_brief = render_hiring_manager_brief(form)
    jd = render_candidate_jd(form)
    scorecard_payload = build_scorecard_payload(form)

    hm_path = target_dir / "hm_brief.md"
    jd_path = target_dir / "candidate_jd.md"
    sc_path = target_dir / "scorecard.json"

    hm_path.write_text(hm_brief, encoding="utf-8")
    jd_path.write_text(jd, encoding="utf-8")
    sc_path.write_text(json.dumps(scorecard_payload, indent=2), encoding="utf-8")

    return {"hm_brief": hm_path, "candidate_jd": jd_path, "scorecard": sc_path}


def generate_from_file(
    intake_path: Path | str, output_base_dir: Path | str | None = None
) -> Dict[str, Path]:
    """Convenience wrapper that loads an intake JSON file."""
    form = load_intake(intake_path)
    return generate_artifacts(form, output_base_dir)


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entrypoint for quick local generation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate HM brief, JD, and scorecard from an intake JSON file."
    )
    parser.add_argument(
        "--input",
        default="examples/intake_sample.json",
        help="Validated intake JSON path.",
    )
    parser.add_argument(
        "--output-root",
        default=None,
        help="Override output root (default: assets/outputs).",
    )
    args = parser.parse_args(argv)

    try:
        paths = generate_from_file(args.input, args.output_root)
    except Exception as exc:  # pragma: no cover - CLI convenience
        parser.error(f"Failed to generate artifacts: {exc}")
        return 1

    for label, path in paths.items():
        print(f"{label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
