"""OAuth2 helpers for Gmail/Workspace with simple token storage."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlencode

import httpx


AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"


@dataclass
class GmailToken:
    access_token: str
    refresh_token: str
    expires_at: datetime
    token_type: str = "Bearer"

    def is_expired(self, skew_seconds: int = 60) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at - timedelta(seconds=skew_seconds)

    def to_dict(self) -> Dict[str, str]:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at.isoformat(),
            "token_type": self.token_type,
        }

    @classmethod
    def from_response(cls, payload: Dict[str, str]) -> "GmailToken":
        expires_in = int(payload.get("expires_in", 3600))
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        return cls(
            access_token=payload["access_token"],
            refresh_token=payload.get("refresh_token", ""),
            token_type=payload.get("token_type", "Bearer"),
            expires_at=expires_at,
        )

    @classmethod
    def from_dict(cls, payload: Dict[str, str]) -> "GmailToken":
        expires_at = datetime.fromisoformat(payload["expires_at"])
        return cls(
            access_token=payload["access_token"],
            refresh_token=payload.get("refresh_token", ""),
            token_type=payload.get("token_type", "Bearer"),
            expires_at=expires_at,
        )


class TokenStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> Optional[GmailToken]:
        if not self.path.exists():
            return None
        with open(self.path, "r", encoding="utf-8") as f:
            return GmailToken.from_dict(json.load(f))

    def save(self, token: GmailToken) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(token.to_dict(), f, indent=2)


class GmailAuth:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        token_store: TokenStore,
        timeout: float = 10.0,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.token_store = token_store
        self.client = http_client or httpx.Client(timeout=timeout)

    def build_auth_url(self, scopes: List[str], state: str = "local") -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
            "scope": " ".join(scopes),
        }
        return f"{AUTH_URL}?{urlencode(params)}"

    def exchange_code(self, code: str) -> GmailToken:
        payload = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        resp = self.client.post(TOKEN_URL, data=payload)
        resp.raise_for_status()
        token = GmailToken.from_response(resp.json())
        self.token_store.save(token)
        return token

    def refresh(self, refresh_token: str) -> GmailToken:
        payload = {
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
        }
        resp = self.client.post(TOKEN_URL, data=payload)
        resp.raise_for_status()
        token = GmailToken.from_response(resp.json())
        if not token.refresh_token:
            token.refresh_token = refresh_token
        self.token_store.save(token)
        return token

    def get_token(self) -> GmailToken:
        token = self.token_store.load()
        if token and not token.is_expired():
            return token
        if token and token.refresh_token:
            return self.refresh(token.refresh_token)
        raise RuntimeError("No Gmail token available. Run OAuth flow first.")

    def close(self) -> None:
        self.client.close()

    @classmethod
    def from_env(cls, token_store: TokenStore) -> "GmailAuth":
        client_id = os.environ.get("GMAIL_CLIENT_ID")
        client_secret = os.environ.get("GMAIL_CLIENT_SECRET")
        redirect_uri = os.environ.get("GMAIL_REDIRECT_URI", "urn:ietf:wg:oauth:2.0:oob")
        if not client_id or not client_secret:
            raise RuntimeError("Set GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET before initializing GmailAuth.")
        return cls(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, token_store=token_store)
