"""Greenhouse note writer with a dry-run mode for tests and demos."""

from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from .greenhouse_client import DEFAULT_BASE_URL, GreenhouseConfig


class GreenhouseWriter:
    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 10.0,
        dry_run: bool = False,
        transport: Optional[httpx.BaseTransport] = None,
    ) -> None:
        if not api_key:
            raise ValueError("Greenhouse API key is required")
        self.dry_run = dry_run
        self.config = GreenhouseConfig(api_key=api_key, base_url=base_url.rstrip("/"), timeout=timeout)
        self.client = httpx.Client(
            base_url=self.config.base_url,
            auth=httpx.BasicAuth(api_key, ""),
            timeout=self.config.timeout,
            headers={"User-Agent": "cayenne-greenhouse-writer"},
            transport=transport,
        )

    def __enter__(self) -> "GreenhouseWriter":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.client.close()

    def post_application_note(
        self,
        application_id: int,
        body: str,
        visibility: str = "private",
        user_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"body": body, "visibility": visibility}
        if user_id is not None:
            payload["user_id"] = user_id

        path = f"/applications/{application_id}/activity_feed/notes"
        if self.dry_run:
            return {"dry_run": True, "path": path, "payload": payload}

        response = self.client.post(path, json=payload)
        response.raise_for_status()
        return response.json()
