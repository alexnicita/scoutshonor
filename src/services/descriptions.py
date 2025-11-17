"""Generate long job descriptions from minimal inputs.

Strategy:
  - Build a rich, structured prompt from user-provided minimal fields.
  - If an LLM provider is configured (LLM_PROVIDER=openai with API key),
    call it to expand into a long-form description.
  - Otherwise, fall back to a deterministic template-based generator that
    produces a comprehensive, readable description suitable for immediate use.
"""

from __future__ import annotations

import os

from ..models.descriptions import JobDescriptionInput, JobDescriptionResponse
from .llm.base import LLMProvider, StubProvider


def _select_provider() -> LLMProvider:
    provider = os.getenv("LLM_PROVIDER", "stub").lower()
    if provider == "openai":
        try:
            from .llm.openai_provider import OpenAIProvider

            return OpenAIProvider()
        except Exception:
            # Fallback to stub on import/network config issues
            return StubProvider()
    return StubProvider()


def _build_prompt(payload: JobDescriptionInput) -> tuple[str, str]:
    system = (
        "You are an expert technical recruiter and hiring manager. "
        "Write clear, inclusive, and compelling long-form job descriptions "
        "that are structured with sections and scannable bullets. Avoid hype."
    )

    # Join helpers
    def j(items):
        return ", ".join(sorted({x.strip() for x in items if x}))

    # Compose a compact but information-rich prompt
    company_line = (
        f"Company: {payload.startup_name or 'A startup'}"
        + (f" | Stage: {payload.stage.value}" if payload.stage else "")
    )
    role_line = (
        f"Role: {payload.title} ({payload.seniority.value})"
        + (f" | Location: {payload.location}" if payload.location else "")
        + (" | Remote OK" if payload.remote_ok else "")
        + (f" | Type: {payload.employment_type}" if payload.employment_type else "")
    )
    scope = []
    if payload.mission:
        scope.append(f"Mission: {payload.mission}")
    if payload.product_description:
        scope.append(f"Product: {payload.product_description}")
    if payload.team_description:
        scope.append(f"Team: {payload.team_description}")

    details = [
        f"Required skills: {j(payload.required_skills)}" if payload.required_skills else None,
        f"Nice-to-have: {j(payload.nice_to_have_skills)}" if payload.nice_to_have_skills else None,
        f"Responsibilities: {j(payload.responsibilities)}" if payload.responsibilities else None,
        f"Minimum experience: {payload.min_years_experience}+ years" if payload.min_years_experience else None,
        f"Compensation: {payload.compensation_range}" if payload.compensation_range else None,
        f"Benefits: {j(payload.benefits)}" if payload.benefits else None,
    ]
    detail_lines = "\n".join([d for d in details if d])
    scope_lines = "\n".join(scope)

    prompt = (
        f"{company_line}\n{role_line}\n\n{scope_lines}\n\n"
        "Produce a long job description with these sections:"
        "\n- Overview (2-3 paragraphs)"
        "\n- What you'll do (6-10 bullets)"
        "\n- What you'll bring (6-10 bullets)"
        "\n- Nice to have (3-6 bullets if present)"
        "\n- Compensation & benefits (1 paragraph + bullets if present)"
        "\n- How to apply (1 short paragraph)\n\n"
        "Ground rules:"
        "\n- Be inclusive and avoid gendered language"
        "\n- Prefer clear, concrete phrasing over buzzwords"
        "\n- Tailor to the seniority level and stage"
        "\n- Use the details below to anchor specifics\n\n" 
        f"Details:\n{detail_lines}\n"
    )
    return system, prompt


def _fallback_template(payload: JobDescriptionInput) -> str:
    # Deterministic, readable long-form description without LLM calls.
    title = f"{payload.title} ({payload.seniority.value})"
    company = payload.startup_name or "our startup"
    loc = payload.location or ("Remote" if payload.remote_ok else "Location TBD")

    def bullets(items, default_intro):
        if not items:
            return f"- {default_intro}"
        return "\n".join(f"- {it}" for it in items)

    req_bullets = bullets(
        payload.required_skills,
        "Strong technical fundamentals relevant to the role",
    )
    nice_bullets = (
        "\n" + bullets(payload.nice_to_have_skills, "Bonus experience that accelerates impact")
        if payload.nice_to_have_skills
        else ""
    )
    resp_bullets = bullets(
        payload.responsibilities,
        "Own impactful projects that move key company metrics",
    )

    overview_extra = []
    if payload.mission:
        overview_extra.append(payload.mission)
    if payload.product_description:
        overview_extra.append(payload.product_description)
    if payload.team_description:
        overview_extra.append(payload.team_description)
    overview_tail = " ".join(overview_extra)

    comp = payload.compensation_range or "Competitive with meaningful equity"
    emp_type = payload.employment_type or "Full-time"
    benefits = (
        "\n".join(f"- {b}" for b in payload.benefits)
        if payload.benefits
        else "- Health, dental, and vision\n- Flexible PTO\n- Remote stipend"
    )

    paragraphs = [
        f"Join {company} as our {title}. You'll help build enduring products and systems while shaping how we work as a team.",
        f"This role is based in {loc}. We value outcomes over hours and create space for deep work. {overview_tail}",
    ]

    what_you_bring = (
        "\n\nWhat you'll bring\n\n- "
        f"{payload.min_years_experience}+ years of relevant experience"
    )
    if req_bullets:
        what_you_bring = f"{what_you_bring}\n{req_bullets}"
    else:
        what_you_bring = f"{what_you_bring}{req_bullets}"

    parts = [
        "Overview\n\n" + "\n\n".join(paragraphs),
        f"\n\nWhat you'll do\n\n{resp_bullets}",
        what_you_bring,
    ]
    if nice_bullets:
        parts.append(f"\n\nNice to have\n\n{nice_bullets}")
    parts.append(
        "\n\nCompensation & benefits\n\n"
        f"- {emp_type}\n- Compensation: {comp}\n{benefits}"
    )
    parts.append(
        "\n\nHow to apply\n\n"
        "- Send your resume and a few lines about what excites you about the role to careers@company.com."
    )
    return "\n".join(parts)


def generate_description(payload: JobDescriptionInput) -> JobDescriptionResponse:
    system, prompt = _build_prompt(payload)
    provider = _select_provider()
    try:
        text = provider.generate(prompt=prompt, system=system).strip()
    except Exception:
        text = ""
    if not text:
        text = _fallback_template(payload)
    title = payload.title if payload.title else "Job Description"
    return JobDescriptionResponse(title=title, description=text)
