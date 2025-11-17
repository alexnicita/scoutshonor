"""Greenhouse Harvest client focused on read-only endpoints.

Supports auth via API key, simple pagination, and normalization helpers for
jobs, candidates, and applications. Intended for fixture-driven tests and
scripts, not production throughput.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urlparse

import httpx


DEFAULT_BASE_URL = "https://harvest.greenhouse.io/v1"


@dataclass
class GreenhouseConfig:
    api_key: str
    base_url: str = DEFAULT_BASE_URL
    page_size: int = 100
    timeout: float = 10.0


class GreenhouseClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        page_size: int = 100,
        timeout: float = 10.0,
        transport: Optional[httpx.BaseTransport] = None,
    ) -> None:
        if not api_key:
            raise ValueError("Greenhouse API key is required")
        self.config = GreenhouseConfig(
            api_key=api_key, base_url=base_url.rstrip("/"), page_size=page_size, timeout=timeout
        )
        self.client = httpx.Client(
            base_url=self.config.base_url,
            auth=httpx.BasicAuth(api_key, ""),
            timeout=self.config.timeout,
            headers={"User-Agent": "cayenne-greenhouse-client"},
            transport=transport,
        )

    # Context manager helpers for tests/scripts.
    def __enter__(self) -> "GreenhouseClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.client.close()

    def list_jobs(self, updated_after: Optional[str] = None) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"per_page": self.config.page_size}
        if updated_after:
            params["updated_after"] = updated_after
        raw = self._paginate("/jobs", params=params)
        return [self._normalize_job(j) for j in raw]

    def list_candidates(self, created_after: Optional[str] = None) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"per_page": self.config.page_size}
        if created_after:
            params["created_after"] = created_after
        raw = self._paginate("/candidates", params=params)
        return [self._normalize_candidate(c) for c in raw]

    def list_applications(self, candidate_id: Optional[int] = None) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"per_page": self.config.page_size}
        if candidate_id:
            params["candidate_id"] = candidate_id
        raw = self._paginate("/applications", params=params)
        return [self._normalize_application(a) for a in raw]

    def _paginate(self, path: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        url: Optional[str] = path
        collected: List[Dict[str, Any]] = []
        params = dict(params or {})

        while url:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, dict) and "data" in payload:
                payload = payload["data"]
            if not isinstance(payload, list):
                raise ValueError(f"Unexpected payload for {url}")
            collected.extend(payload)
            next_link = response.links.get("next", {}).get("url") or self._extract_next_link(response.headers)
            url = next_link
            params = None
        return collected

    @staticmethod
    def _extract_next_link(headers: Dict[str, str]) -> Optional[str]:
        link_header = headers.get("Link") or headers.get("link")
        if not link_header:
            return None
        # Format: <https://.../page=2>; rel="next"
        for part in link_header.split(","):
            segs = part.split(";")
            if len(segs) < 2:
                continue
            url_part = segs[0].strip()
            rel = ";".join(segs[1:]).strip()
            if 'rel="next"' in rel:
                return url_part.strip("<>")
        return None

    @staticmethod
    def _normalize_job(job: Dict[str, Any]) -> Dict[str, Any]:
        departments = [d.get("name") for d in job.get("departments", [])]
        offices = [o.get("name") for o in job.get("offices", [])]
        openings = [o.get("id") for o in job.get("openings", [])]
        return {
            "id": job.get("id"),
            "name": job.get("name"),
            "status": job.get("status") or job.get("internal_job_id"),
            "departments": [d for d in departments if d],
            "offices": [o for o in offices if o],
            "opening_ids": [oid for oid in openings if oid is not None],
        }

    @staticmethod
    def _normalize_candidate(cand: Dict[str, Any]) -> Dict[str, Any]:
        emails = [e.get("value") for e in cand.get("email_addresses", [])]
        phones = [p.get("value") for p in cand.get("phone_numbers", [])]
        return {
            "id": cand.get("id"),
            "first_name": cand.get("first_name"),
            "last_name": cand.get("last_name"),
            "company": cand.get("company"),
            "title": cand.get("title"),
            "emails": [e for e in emails if e],
            "phones": [p for p in phones if p],
        }

    @staticmethod
    def _normalize_application(app: Dict[str, Any]) -> Dict[str, Any]:
        job_ids: List[int] = []
        candidate_id = app.get("candidate_id")
        if "jobs" in app:
            job_ids = [j.get("id") for j in app.get("jobs", []) if j.get("id") is not None]
        elif app.get("job_id") is not None:
            job_ids = [app["job_id"]]
        source = None
        if app.get("source"):
            source = app["source"].get("public_name") or app["source"].get("name")
        return {
            "id": app.get("id"),
            "candidate_id": candidate_id,
            "job_ids": job_ids,
            "stage": (app.get("stage") or {}).get("name") if isinstance(app.get("stage"), dict) else app.get("stage"),
            "source": source,
        }


def is_greenhouse_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.netloc.endswith("greenhouse.io")
