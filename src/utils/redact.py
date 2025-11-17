"""PII redaction helpers for logs and debug output.

Purpose:
    Strip emails, phone numbers, and sensitive keys from nested payloads before
    emitting logs or traces. Keeps testing deterministic by using fixed tokens.
Dependencies:
    Standard library only.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List


EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")
PII_KEYS = {
    "full_name",
    "name",
    "email",
    "phone",
    "contact",
    "linkedin_url",
    "subject",
    "body",
}


def _redact_string(value: str) -> str:
    value = EMAIL_RE.sub("[REDACTED_EMAIL]", value)
    value = PHONE_RE.sub("[REDACTED_PHONE]", value)
    return value


def redact_value(value: Any, key_context: str | None = None) -> Any:
    """Redact a single value, optionally considering the parent key name."""
    if isinstance(value, str):
        if key_context and key_context.lower() in PII_KEYS:
            return "[REDACTED]"
        return _redact_string(value)

    if isinstance(value, dict):
        return {k: redact_value(v, k) for k, v in value.items()}

    if isinstance(value, list):
        return [redact_value(v, key_context) for v in value]

    return value


def redact_payload(payload: Dict[str, Any] | List[Any]) -> Dict[str, Any] | List[Any]:
    """Redact the provided dict or list payload in a defensive copy."""
    if isinstance(payload, dict):
        return {k: redact_value(v, k) for k, v in payload.items()}
    if isinstance(payload, list):
        return [redact_value(v, None) for v in payload]
    return redact_value(payload, None)
