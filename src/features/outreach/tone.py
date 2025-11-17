"""Tone and personalization schema for outreach copy.

Defines structured preferences for tone and message personalization so
sequence engines or templates can render consistent outreach across
channels without ad-hoc string building.
"""

from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, Field, field_validator

from ...models.common import Tone


class PersonalizationHints(BaseModel):
    """Inputs used to tailor outreach to a candidate."""

    candidate_name: str
    role_title: str
    startup_name: str
    differentiators: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    call_to_action: str = "Should we schedule time to talk?"

    def headline(self) -> str:
        differentiator = ", ".join(self.differentiators[:2])
        if differentiator:
            return f"{self.startup_name} needs a {self.role_title} ({differentiator})"
        return f"{self.startup_name} needs a {self.role_title}"


class ToneProfile(BaseModel):
    """Tone preferences that shape outreach language."""

    tone: Tone
    formality: Literal["casual", "balanced", "formal"] = "balanced"
    brevity: Literal["short", "medium", "long"] = "medium"
    signature: str = "— Recruiting Team"
    use_personal_detail: bool = True

    @field_validator("signature")
    @classmethod
    def ensure_signature(cls, value: str) -> str:
        return value.strip() or "— Recruiting Team"

    def apply(self, personalization: PersonalizationHints) -> str:
        """Render a short personalized blurb using the tone preferences."""

        opener = _opener_for_tone(self.tone, personalization.candidate_name)
        detail = ""
        if self.use_personal_detail and personalization.interests:
            detail = f"I noticed your interest in {personalization.interests[0]}."
        differentiator = personalization.headline()
        cta = personalization.call_to_action
        closing = self.signature

        body_lines = [opener, differentiator, detail, cta, closing]
        if self.brevity == "short":
            body_lines = [opener, cta, closing]
        elif self.brevity == "long":
            body_lines.insert(2, "We think you'd level up the team from day one.")

        # Drop any empty lines to avoid ragged formatting
        return "\n".join([line for line in body_lines if line.strip()])


def _opener_for_tone(tone: Tone, candidate_name: str) -> str:
    first_name = candidate_name.split()[0] if candidate_name else "there"
    if tone == "friendly":
        return f"Hi {first_name}! I hope you're having a great week."
    if tone == "concise":
        return f"{first_name}, quick note about a role."
    return f"Hello {first_name}, reaching out about a role aligned to you."
