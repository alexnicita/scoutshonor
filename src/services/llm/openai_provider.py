"""OpenAI-compatible provider using HTTPX.

Purpose:
  Minimal HTTP client for Chat Completions that works with OpenAI and
  OpenAI-compatible servers (via `OPENAI_BASE_URL`). Only imported at runtime
  when selected to avoid hard dependency on vendor SDKs.
"""

from __future__ import annotations

import os
from typing import Optional

import httpx

from .base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self, model: Optional[str] = None, timeout: float = 20.0):
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.timeout = timeout

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set")

        url = f"{self.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self.model,
            "messages": messages,
            # Keep responses concise but useful; model will expand based on prompt
            "temperature": float(os.getenv("OPENAI_TEMPERATURE", 0.3)),
        }

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return content or ""
