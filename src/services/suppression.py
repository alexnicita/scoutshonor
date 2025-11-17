"""In-memory suppression list to honor opt-outs and bounces."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, List, Set


@dataclass
class SuppressionEvent:
    email: str
    reason: str
    timestamp: datetime

    def to_dict(self) -> Dict[str, str]:
        payload = asdict(self)
        payload["timestamp"] = self.timestamp.isoformat()
        return payload


class SuppressionStore:
    def __init__(self) -> None:
        self._suppressed: Set[str] = set()
        self.audit_log: List[SuppressionEvent] = []

    def suppress(self, email: str, reason: str = "manual") -> None:
        normalized = self._normalize(email)
        self._suppressed.add(normalized)
        self.audit_log.append(
            SuppressionEvent(
                email=normalized, reason=reason, timestamp=datetime.now(timezone.utc)
            )
        )

    def is_suppressed(self, email: str) -> bool:
        return self._normalize(email) in self._suppressed

    def remove(self, email: str) -> None:
        normalized = self._normalize(email)
        self._suppressed.discard(normalized)

    def list(self) -> List[str]:
        return sorted(self._suppressed)

    def reset(self) -> None:
        self._suppressed.clear()
        self.audit_log.clear()

    @staticmethod
    def _normalize(email: str) -> str:
        return email.strip().lower()


suppression_store = SuppressionStore()
