"""Summarization helpers with schema-backed responses."""

from __future__ import annotations

from typing import List, Protocol
from pydantic import BaseModel, Field


class SummaryProvider(Protocol):
    """Callable text generator used by the summarizer."""

    name: str

    def complete(self, prompt: str) -> str:
        """Return model output for the given prompt."""


class SummaryChunk(BaseModel):
    """Atomic unit of content to summarize."""

    id: str
    text: str
    source: str = Field(default="unknown", description="Origin of the text")


class SummaryResponse(BaseModel):
    """Schema returned by summarization routines."""

    summary: str
    combined_sources: List[str]
    token_estimate: int
    provider: str


def _build_prompt(chunks: List[SummaryChunk], instruction: str | None = None) -> str:
    base_instruction = instruction or "Summarize candidate signals and risks as bullet points."
    lines = [base_instruction, "", "Context:"]
    for chunk in chunks:
        lines.append(f"- [{chunk.source}] ({chunk.id}): {chunk.text}")
    lines.append("")
    lines.append("Return concise, factual notes.")
    return "\n".join(lines)


def _estimate_tokens(text: str) -> int:
    return len(text.split())


class Summarizer:
    """Generate summaries with light prompt construction."""

    def __init__(self, provider: SummaryProvider):
        self.provider = provider

    def summarize(
        self, chunks: List[SummaryChunk], instruction: str | None = None
    ) -> SummaryResponse:
        if not chunks:
            raise ValueError("no content provided for summarization")

        prompt = _build_prompt(chunks, instruction)
        output = self.provider.complete(prompt)
        combined_sources = sorted({chunk.source for chunk in chunks})
        token_estimate = sum(_estimate_tokens(chunk.text) for chunk in chunks) + _estimate_tokens(output)
        return SummaryResponse(
            summary=output.strip(),
            combined_sources=combined_sources,
            token_estimate=token_estimate,
            provider=self.provider.name,
        )

