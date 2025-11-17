"""LLM provider abstraction.

Purpose:
  Provide a tiny interface for invoking an LLM so the app can swap
  implementations (e.g., OpenAI, local, stub) without changing callers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """Return the generated text for a prompt."""
        raise NotImplementedError


class StubProvider(LLMProvider):
    """Deterministic, offline stub used when no API credentials are present."""

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        # Very simple echo-style expansion; callers should pass a rich prompt.
        # Keep deterministic for tests.
        header = (system or "").strip()
        body = prompt.strip()
        parts = [p for p in [header, body] if p]
        return "\n\n".join(parts)

