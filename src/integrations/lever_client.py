"""Lightweight Lever client with parity to the Greenhouse reader."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

DEFAULT_BASE_URL = "https://api.lever.co/v1"


class LeverClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 10.0,
        transport: Optional[httpx.BaseTransport] = None,
    ) -> None:
        if not api_key:
            raise ValueError("Lever API key is required")
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(
            base_url=self.base_url,
            auth=httpx.BasicAuth(api_key, ""),
            timeout=timeout,
            headers={"User-Agent": "cayenne-lever-client"},
            transport=transport,
        )

    def __enter__(self) -> "LeverClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.client.close()

    def list_postings(self) -> List[Dict[str, Any]]:
        resp = self.client.get("/postings")
        resp.raise_for_status()
        payload = resp.json()
        return [self._normalize_posting(p) for p in payload.get("data", payload)]

    def list_candidates(self) -> List[Dict[str, Any]]:
        resp = self.client.get("/candidates")
        resp.raise_for_status()
        payload = resp.json()
        return [self._normalize_candidate(c) for c in payload.get("data", payload)]

    def list_applications(self) -> List[Dict[str, Any]]:
        resp = self.client.get("/applications")
        resp.raise_for_status()
        payload = resp.json()
        return [self._normalize_application(a) for a in payload.get("data", payload)]

    @staticmethod
    def _normalize_posting(posting: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": posting.get("id"),
            "team": posting.get("team"),
            "title": posting.get("text") or posting.get("title"),
            "department": posting.get("categories", {}).get("department"),
            "location": posting.get("categories", {}).get("location"),
            "status": posting.get("state") or posting.get("status"),
        }

    @staticmethod
    def _normalize_candidate(candidate: Dict[str, Any]) -> Dict[str, Any]:
        emails = candidate.get("emails") or []
        phones = candidate.get("phones") or []
        return {
            "id": candidate.get("id"),
            "name": candidate.get("name"),
            "headline": candidate.get("headline"),
            "email": emails[0] if emails else None,
            "phones": phones,
            "stage": candidate.get("stage"),
        }

    @staticmethod
    def _normalize_application(app: Dict[str, Any]) -> Dict[str, Any]:
        attachments = app.get("files") or []
        return {
            "id": app.get("id"),
            "opportunity_id": app.get("opportunityId") or app.get("opportunity_id"),
            "posting_id": app.get("posting") or app.get("postingId"),
            "status": app.get("stage") or app.get("status"),
            "files": attachments,
        }
