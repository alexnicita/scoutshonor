"""
Structured logging helpers.

This module keeps logging dependency-free by using the Python stdlib. It exposes
configure_logging() to initialize formatting once and get_logger() to produce
context-aware loggers that append key/value fields to each message.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict


def _default_level() -> str:
    return os.getenv("LOG_LEVEL", "INFO").upper()


def _log_format() -> str:
    return os.getenv("LOG_FORMAT", "plain").lower()


def configure_logging(level: str | None = None) -> None:
    """
    Configure root logging with a simple formatter. Idempotent: safe to call
    multiple times without stacking handlers.
    """
    resolved_level = (level or _default_level()).upper()
    root_logger = logging.getLogger()
    root_logger.setLevel(resolved_level)
    if root_logger.handlers:
        return

    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)


def _stringify(value: Any) -> str:
    try:
        if isinstance(value, str):
            return value
        return json.dumps(value, default=str, separators=(",", ":"))
    except TypeError:
        return str(value)


class StructuredLogger(logging.LoggerAdapter):
    """A thin adapter that appends context fields to each log message."""

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        extra = kwargs.pop("extra", {})
        context = {**self.extra, **extra}

        if _log_format() == "structured":
            payload: Dict[str, Any] = {"event": msg, **context}
            msg = json.dumps(payload, default=str)
        elif context:
            kv_pairs = " ".join(
                f"{key}={_stringify(val)}" for key, val in context.items()
            )
            msg = f"{msg} | {kv_pairs}"

        kwargs.setdefault("stacklevel", 2)
        return msg, kwargs


def get_logger(name: str, **context: Any) -> StructuredLogger:
    """
    Return a contextual logger using the configured format. Additional context
    can be provided at call time via the extra= kwarg.
    """
    configure_logging()
    base_logger = logging.getLogger(name)
    return StructuredLogger(base_logger, context)
