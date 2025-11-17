"""Gmail sender with dry-run rendering and suppression enforcement."""

from __future__ import annotations

import base64
from email.message import EmailMessage
from typing import Dict, List, Optional

import httpx

from .gmail_auth import GmailAuth
from ..services.suppression import SuppressionStore, suppression_store


class SuppressedRecipientError(RuntimeError):
    pass


class GmailSender:
    def __init__(
        self,
        auth: GmailAuth,
        from_address: str = "me",
        api_base: str = "https://gmail.googleapis.com/gmail/v1",
        dry_run: bool = False,
        suppression: Optional[SuppressionStore] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        self.auth = auth
        self.from_address = from_address
        self.api_base = api_base.rstrip("/")
        self.dry_run = dry_run
        self.http_client = http_client or httpx.Client(timeout=10.0)
        self.suppression = suppression or suppression_store

    def build_message(
        self,
        to: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        unsubscribe_link: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> EmailMessage:
        msg = EmailMessage()
        msg["To"] = to
        msg["From"] = self.from_address
        msg["Subject"] = subject
        if cc:
            msg["Cc"] = ", ".join(cc)
        if bcc:
            msg["Bcc"] = ", ".join(bcc)
        if unsubscribe_link:
            msg["List-Unsubscribe"] = f"<{unsubscribe_link}>"
            msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
        if headers:
            for key, value in headers.items():
                msg[key] = value

        msg.set_content(body_text)
        if body_html:
            msg.add_alternative(body_html, subtype="html")
        return msg

    def send_email(
        self,
        to: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        unsubscribe_link: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, object]:
        if self.suppression and self.suppression.is_suppressed(to):
            raise SuppressedRecipientError(f"{to} is suppressed; refusing to send.")

        message = self.build_message(
            to=to,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            cc=cc,
            bcc=bcc,
            unsubscribe_link=unsubscribe_link,
            headers=headers,
        )
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        payload = {"raw": raw_message}

        if self.dry_run:
            return {"dry_run": True, "payload": payload, "subject": subject, "to": to}

        token = self.auth.get_token()
        headers = {"Authorization": f"{token.token_type} {token.access_token}"}
        response = self.http_client.post(f"{self.api_base}/users/me/messages/send", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
