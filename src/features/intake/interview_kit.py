"""Role-specific interview kit generator based on an intake form."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .schema import IntakeForm, ScorecardCompetency
from .generate import _output_dir


def _question_block(competency: ScorecardCompetency) -> str:
    signals = "\n".join(f"  - {signal}" for signal in competency.signals) or "  - TBD"
    knockout = (
        "\n".join(f"  - {q}" for q in competency.knockout_questions)
        if competency.knockout_questions
        else "  - None configured"
    )
    return (
        f"### {competency.name} ({competency.weight} weight)\n"
        f"- Signals to probe:\n{signals}\n"
        f"- Knockout questions:\n{knockout}\n"
        f"- Scoring guidance: 1 = misses signals, 3 = meets expectations, 5 = exemplar with evidence.\n"
    )


def render_interview_kit(form: IntakeForm) -> str:
    intro = (
        f"# Interview Kit — {form.role_title}\n"
        f"## Context\n"
        f"- Mission: {form.mission}\n"
        f"- Goals: {', '.join(form.goals) if form.goals else 'TBD'}\n"
        f"- Success metrics: {', '.join(form.success_metrics) if form.success_metrics else 'TBD'}\n"
        f"- Interview panel: {', '.join(form.interview_panel) if form.interview_panel else 'TBD'}\n"
    )
    kickoff = (
        "## Kickoff prompts\n"
        "- Walk me through your recent role and team scope.\n"
        "- How do you decide where to spend platform/infra capacity vs. feature asks?\n"
    )
    competency_blocks = "\n".join(_question_block(c) for c in form.scorecard) or (
        "### To be defined\n- Add competencies to the intake to generate a kit."
    )
    wrap = (
        "## Closing\n"
        "- Share any concerns or risks you spotted.\n"
        "- Provide a score per competency plus overall signal.\n"
    )
    return "\n".join([intro, kickoff, competency_blocks, wrap])


def generate_interview_kit(
    form: IntakeForm, output_base_dir: Path | str | None = None
) -> Dict[str, Path]:
    """Write a Markdown interview kit alongside other intake artifacts."""
    target_dir = _output_dir(form.role_id, output_base_dir)
    kit = render_interview_kit(form)
    kit_path = target_dir / "interview_kit.md"
    kit_path.write_text(kit, encoding="utf-8")
    return {"interview_kit": kit_path}


def generate_from_intake_path(
    intake_path: Path | str, output_base_dir: Path | str | None = None
) -> Dict[str, Path]:
    from .schema import load_intake

    form = load_intake(intake_path)
    return generate_interview_kit(form, output_base_dir)


__all__: List[str] = [
    "generate_interview_kit",
    "render_interview_kit",
    "generate_from_intake_path",
]
