"""Outreach message generator.

Template-driven for now; later swap in an LLM provider behind the same interface.
"""

from __future__ import annotations

from typing import List

from ..models.candidate import Candidate
from ..models.role import Role
from ..models.outreach import OutreachMessage
from ..models.common import Tone, Channel


def _tone_line(tone: Tone) -> str:
    if tone == "friendly":
        return "I loved your background and thought of you for a role."
    if tone == "concise":
        return "Quick note about a role that fits your background."
    return "Reaching out about a role aligned with your experience."


def _subject(role: Role, startup_name: str) -> str:
    return f"{role.title} @ {startup_name}"


def _body(
    candidate: Candidate,
    role: Role,
    startup_name: str,
    tone: Tone,
    cal_link: str | None,
) -> str:
    greeting = f"Hi {candidate.full_name.split()[0]},"
    opener = _tone_line(tone)
    highlights: List[str] = []
    if role.required_skills:
        highlights.append(f"stack: {', '.join(role.required_skills[:5])}")
    if role.responsibilities:
        highlights.append(f"scope: {', '.join(role.responsibilities[:3])}")
    bullet = " | ".join(highlights)
    closing = "If you're open to it, I'd love to share more."
    if cal_link:
        closing += f" Grab a time: {cal_link}"

    lines = [
        greeting,
        "",
        opener,
        f"We're hiring a {role.title} at {startup_name}.",
        (f"Highlights → {bullet}" if bullet else ""),
        "",
        closing,
        "— Recruiting Team",
    ]
    return "\n".join([line for line in lines if line is not None])


def generate_messages(
    candidate: Candidate,
    role: Role,
    startup_name: str,
    tone: Tone,
    channels: List[Channel],
    cal_link: str | None,
) -> List[OutreachMessage]:
    msgs: List[OutreachMessage] = []
    subject = _subject(role, startup_name)
    body = _body(candidate, role, startup_name, tone, cal_link)
    for ch in channels:
        msgs.append(OutreachMessage(channel=ch, subject=subject, body=body))
    return msgs
