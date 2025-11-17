"""Outreach sequencing engine with reply-aware suppression.

Provides a minimal two-step sequence suitable for email or LinkedIn,
and hooks for routing replies plus emitting lightweight metrics when a
reply arrives. Keeps state in-memory to stay deterministic in tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable, Dict, Iterable, List, Optional

from ...models.common import Channel

MetricsHook = Callable[[str, Dict[str, object]], None]


@dataclass(frozen=True)
class SequenceStep:
    name: str
    channel: Channel
    delay_hours: int
    template: str


DEFAULT_SEQUENCE: List[SequenceStep] = [
    SequenceStep(name="intro", channel="email", delay_hours=0, template="intro_v1"),
    SequenceStep(
        name="nudge", channel="email", delay_hours=48, template="follow_up_v1"
    ),
]


class OutreachSequenceEngine:
    """Calculates pending outreach steps with reply suppression."""

    def __init__(
        self,
        steps: Iterable[SequenceStep] | None = None,
        metrics_hook: Optional[MetricsHook] = None,
    ) -> None:
        self.steps = list(steps) if steps is not None else list(DEFAULT_SEQUENCE)
        self.metrics_hook = metrics_hook
        self._sent: Dict[str, List[str]] = {}
        self._reply_received_at: Dict[str, datetime] = {}

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def mark_sent(self, candidate_id: str, step_name: str) -> None:
        sent_steps = self._sent.setdefault(candidate_id, [])
        if step_name not in sent_steps:
            sent_steps.append(step_name)

    def register_reply(self, candidate_id: str, channel: Channel) -> None:
        self._reply_received_at[candidate_id] = self._now()
        if self.metrics_hook:
            self.metrics_hook(
                "reply_recorded",
                {"candidate_id": candidate_id, "channel": channel, "suppressed": True},
            )

    def pending_steps(
        self, candidate_id: str, start_time: Optional[datetime] = None
    ) -> List[dict]:
        """Return sequence steps that should still send.

        Any reply suppresses remaining steps. Sent steps are skipped.
        """

        start = start_time or self._now()
        reply_at = self._reply_received_at.get(candidate_id)
        pending: List[dict] = []
        for step in self.steps:
            if step.name in self._sent.get(candidate_id, []):
                continue
            scheduled_at = start + timedelta(hours=step.delay_hours)
            if reply_at and reply_at <= scheduled_at:
                continue
            pending.append(
                {
                    "candidate_id": candidate_id,
                    "channel": step.channel,
                    "template": step.template,
                    "send_at": scheduled_at,
                }
            )
        return pending


class ReplyRouter:
    """Routes replies to the correct owner and emits metrics hooks."""

    def __init__(
        self,
        ownership_index: Dict[str, str],
        metrics_hook: Optional[MetricsHook] = None,
    ) -> None:
        self.ownership_index = ownership_index
        self.metrics_hook = metrics_hook

    def route(self, candidate_id: str, channel: Channel, body: str) -> dict:
        owner = self.ownership_index.get(candidate_id) or self.ownership_index.get(
            "default", "unassigned"
        )
        routed = {
            "candidate_id": candidate_id,
            "owner": owner,
            "channel": channel,
            "summary": body[:140],
        }
        if self.metrics_hook:
            self.metrics_hook("reply_routed", routed)
        return routed
