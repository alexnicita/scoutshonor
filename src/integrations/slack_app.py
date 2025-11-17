"""Minimal Slack app helper for posting messages and handling slash commands."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import httpx

from ..services.repositories import repo


@dataclass
class SlashCommandResult:
    text: str
    response_type: str = "ephemeral"
    blocks: Optional[List[Dict[str, object]]] = None

    def to_dict(self) -> Dict[str, object]:
        payload: Dict[str, object] = {
            "text": self.text,
            "response_type": self.response_type,
        }
        if self.blocks:
            payload["blocks"] = self.blocks
        return payload


class SlackApp:
    def __init__(
        self,
        bot_token: str,
        signing_secret: Optional[str] = None,
        base_url: str = "https://slack.com/api",
        dry_run: bool = False,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        if not bot_token:
            raise ValueError("Slack bot token is required.")
        self.bot_token = bot_token
        self.signing_secret = signing_secret
        self.base_url = base_url.rstrip("/")
        self.dry_run = dry_run
        self.http_client = http_client or httpx.Client(timeout=10.0)

    def post_message(
        self, channel: str, text: str, blocks: Optional[List[Dict[str, object]]] = None
    ) -> Dict[str, object]:
        payload: Dict[str, object] = {"channel": channel, "text": text}
        if blocks:
            payload["blocks"] = blocks
        if self.dry_run:
            return {"dry_run": True, "payload": payload}

        resp = self.http_client.post(
            f"{self.base_url}/chat.postMessage",
            headers=self._headers(),
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()

    def handle_slash_command(
        self, action: str, text: str, user_id: str, channel_id: str
    ) -> SlashCommandResult:
        action = (action or "").strip()
        if not action:
            # Assume first token of text is the action for `/recruit <action> ...`
            parts = text.split()
            action = parts[0] if parts else ""
            text = " ".join(parts[1:]) if len(parts) > 1 else ""

        if action in ("draft-outreach", "draft"):
            return self._draft_outreach(text, user_id)
        if action in ("add-note", "note"):
            return self._add_note(text, user_id)
        if action in ("who-is-stuck", "stuck"):
            return self._who_is_stuck()

        return SlashCommandResult(
            text=f"Unknown command `{action}`. Try draft-outreach, add-note, or who-is-stuck."
        )

    def _draft_outreach(self, text: str, user_id: str) -> SlashCommandResult:
        prompt = text or "role: <title> | candidate: <name>"
        body = (
            f"Hi <@{user_id}>, here's a quick outreach stub based on `{prompt}`:\n"
            "- Subject: Quick chat about the role\n"
            "- Body: intro, 2 bullets on fit, and a clear CTA.\n"
            "Swap in personalization before sending."
        )
        return SlashCommandResult(text=body)

    def _add_note(self, text: str, user_id: str) -> SlashCommandResult:
        body = (
            f"Note captured from <@{user_id}>: {text or '[no text provided]'}. "
            "Sync to the ATS via the API client when ready."
        )
        return SlashCommandResult(text=body, response_type="in_channel")

    def _who_is_stuck(self) -> SlashCommandResult:
        roles = repo.list_roles()
        candidates = repo.list_candidates()
        body_lines = [
            f"Roles in-flight: {len(roles)}",
            f"Candidates tracked: {len(candidates)}",
            "Stalled >5 days: tracking not yet implemented; add stage timestamps to enable.",
        ]
        return SlashCommandResult(text="\n".join(body_lines))

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json; charset=utf-8",
        }
