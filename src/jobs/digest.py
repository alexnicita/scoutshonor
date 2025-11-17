"""Daily digest job for Slack or stdout."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from ..services.repositories import repo
from ..integrations.slack_app import SlackApp


def build_digest(stale_days: int = 5) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    roles = repo.list_roles()
    candidates = repo.list_candidates()
    lines = [
        f"Recruiting digest — {now}",
        f"Roles in-flight: {len(roles)}",
        f"Candidates tracked: {len(candidates)}",
        f"Candidates stalled >{stale_days} days: tracking not yet implemented; add stage timestamps to enable.",
        "Missing scorecards: not yet recorded; add scorecard tracking to surface gaps.",
    ]
    if roles:
        lines.append("")
        lines.append("Role summary:")
        for role in roles:
            lines.append(f"- {role.title} (startup {role.startup_id}) — required skills: {', '.join(role.required_skills) or 'n/a'}")
    return "\n".join(lines)


def run_digest(slack_channel: Optional[str] = None, slack_bot_token: Optional[str] = None) -> str:
    digest_text = build_digest()
    print(digest_text)
    if slack_channel and slack_bot_token:
        app = SlackApp(bot_token=slack_bot_token)
        app.post_message(channel=slack_channel, text=digest_text)
    return digest_text


if __name__ == "__main__":
    import os

    run_digest(slack_channel=os.environ.get("SLACK_CHANNEL_ID"), slack_bot_token=os.environ.get("SLACK_BOT_TOKEN"))
