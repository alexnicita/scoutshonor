import json
from datetime import datetime, timezone, timedelta

from src.features.outreach.sequence import (
    OutreachSequenceEngine,
    ReplyRouter,
    DEFAULT_SEQUENCE,
)
from src.features.outreach.tone import PersonalizationHints, ToneProfile


def load_personalization() -> PersonalizationHints:
    with open("tests/fixtures/personalization.json", encoding="utf-8") as f:
        payload = json.load(f)
    return PersonalizationHints(**payload)


def test_tone_profile_renders_personalization():
    personalization = load_personalization()
    profile = ToneProfile(tone="friendly", brevity="long", signature="— Founder")
    message = profile.apply(personalization)

    assert personalization.candidate_name.split()[0] in message
    assert personalization.role_title in message
    assert "— Founder" in message
    # Long tone should include the extra line
    assert "level up the team" in message


def test_sequence_engine_suppresses_after_reply():
    events = []

    def push_metric(name, data):
        events.append((name, data))

    engine = OutreachSequenceEngine(metrics_hook=push_metric)
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)

    pending = engine.pending_steps(candidate_id="cand-123", start_time=start)
    assert len(pending) == len(DEFAULT_SEQUENCE)
    assert pending[0]["send_at"] == start

    # Simulate reply before follow-up goes out
    engine._now = lambda: start + timedelta(hours=1)  # type: ignore[attr-defined]
    engine.register_reply(candidate_id="cand-123", channel="email")

    pending_after_reply = engine.pending_steps(
        candidate_id="cand-123", start_time=start
    )
    assert len(pending_after_reply) == 1
    assert pending_after_reply[0]["template"] == "intro_v1"
    assert events and events[0][0] == "reply_recorded"


def test_reply_router_defaults_and_metrics():
    routed_events = []

    def metrics(name, data):
        routed_events.append((name, data))

    router = ReplyRouter(
        ownership_index={
            "cand-123": "ae@scoutshonor.ai",
            "default": "ops@scoutshonor.ai",
        },
        metrics_hook=metrics,
    )
    payload = router.route(
        candidate_id="cand-unknown",
        channel="linkedin",
        body="Thanks for reaching out, I'm interested.",
    )

    assert payload["owner"] == "ops@scoutshonor.ai"
    assert payload["summary"].startswith("Thanks for reaching out")
    assert routed_events and routed_events[0][0] == "reply_routed"
