"""Polling helpers for Gmail to catch replies, bounces, and OOO messages."""

from __future__ import annotations

from dataclasses import dataclass
from email.utils import getaddresses
from typing import Dict, List, Optional

import httpx

from .gmail_auth import GmailAuth
from ..services.suppression import SuppressionStore, suppression_store


@dataclass
class InteractionEvent:
    message_id: str
    thread_id: str
    event: str
    reason: Optional[str]
    addresses: List[str]
    snippet: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "message_id": self.message_id,
            "thread_id": self.thread_id,
            "event": self.event,
            "reason": self.reason,
            "addresses": self.addresses,
            "snippet": self.snippet,
        }


class GmailPoller:
    def __init__(
        self,
        auth: GmailAuth,
        api_base: str = "https://gmail.googleapis.com/gmail/v1",
        label: str = "INBOX",
        suppression: Optional[SuppressionStore] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        self.auth = auth
        self.api_base = api_base.rstrip("/")
        self.label = label
        self.suppression = suppression or suppression_store
        self.http_client = http_client or httpx.Client(timeout=10.0)

    def poll(self, query: str = "", max_results: int = 25) -> List[InteractionEvent]:
        token = self.auth.get_token()
        headers = {"Authorization": f"{token.token_type} {token.access_token}"}
        params = {"labelIds": self.label, "maxResults": max_results}
        if query:
            params["q"] = query
        response = self.http_client.get(
            f"{self.api_base}/users/me/messages", params=params, headers=headers
        )
        response.raise_for_status()
        messages = response.json().get("messages", [])

        events: List[InteractionEvent] = []
        for msg in messages:
            detail = self._fetch_message(msg["id"], headers=headers)
            event = self._classify_message(detail)
            events.append(event)
            if event.event == "bounce" and self.suppression:
                for addr in event.addresses:
                    self.suppression.suppress(addr, reason="bounce")
        return events

    def _fetch_message(
        self, message_id: str, headers: Dict[str, str]
    ) -> Dict[str, object]:
        resp = self.http_client.get(
            f"{self.api_base}/users/me/messages/{message_id}",
            params={
                "format": "metadata",
                "metadataHeaders": [
                    "Subject",
                    "From",
                    "To",
                    "Cc",
                    "Bcc",
                    "Auto-Submitted",
                ],
            },
            headers=headers,
        )
        resp.raise_for_status()
        return resp.json()

    def _classify_message(self, message: Dict[str, object]) -> InteractionEvent:
        headers = {
            h["name"].lower(): h["value"]
            for h in message.get("payload", {}).get("headers", [])
        }
        snippet = message.get("snippet", "")
        addresses = self._addresses_from_headers(headers)
        if self._is_bounce(headers, snippet):
            reason = "bounce"
            event = "bounce"
        elif self._is_out_of_office(headers):
            reason = "out_of_office"
            event = "out_of_office"
        elif "in-reply-to" in headers or "references" in headers:
            reason = "reply"
            event = "reply"
        else:
            reason = None
            event = "unknown"
        return InteractionEvent(
            message_id=message.get("id", ""),
            thread_id=message.get("threadId", ""),
            event=event,
            reason=reason,
            addresses=addresses,
            snippet=snippet,
        )

    @staticmethod
    def _addresses_from_headers(headers: Dict[str, str]) -> List[str]:
        combined = []
        for field in ("to", "from", "cc", "bcc", "delivered-to", "x-failed-recipients"):
            if field in headers:
                combined.append(headers[field])
        parsed = [addr for _, addr in getaddresses(combined) if addr]
        normalized = [addr.lower() for addr in parsed]
        return sorted(set(normalized))

    @staticmethod
    def _is_bounce(headers: Dict[str, str], snippet: str) -> bool:
        subject = headers.get("subject", "").lower()
        sender = headers.get("from", "").lower()
        if "delivery status notification" in subject or "failure notice" in subject:
            return True
        if "mailer-daemon" in sender or "postmaster@" in sender:
            return True
        if "delivery has failed" in snippet.lower():
            return True
        return False

    @staticmethod
    def _is_out_of_office(headers: Dict[str, str]) -> bool:
        subject = headers.get("subject", "").lower()
        auto_submitted = headers.get("auto-submitted", "").lower()
        if "out of office" in subject or "ooo" in subject:
            return True
        if auto_submitted and auto_submitted != "no":
            return True
        return False
