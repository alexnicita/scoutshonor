"""Embedding interfaces and cosine utilities.

Provides a lightweight contract for embedding providers plus helpers for
measuring similarity and normalizing vectors. Designed for offline unit tests
with deterministic providers.
"""

from __future__ import annotations

from math import sqrt
from typing import List, Protocol


class EmbeddingProvider(Protocol):
    """Minimal contract for embedding providers."""

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Return one embedding vector per input text."""


def _dot(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _magnitude(vec: List[float]) -> float:
    return sqrt(_dot(vec, vec))


def normalize(vec: List[float]) -> List[float]:
    """Return a unit-length copy of the vector."""
    mag = _magnitude(vec)
    if mag == 0:
        raise ValueError("cannot normalize zero vector")
    return [v / mag for v in vec]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if len(a) != len(b):
        raise ValueError("vector lengths must match")
    denom = _magnitude(a) * _magnitude(b)
    if denom == 0:
        raise ValueError("cosine similarity undefined for zero vectors")
    return _dot(a, b) / denom


def batch_cosine_similarity(
    queries: List[List[float]], docs: List[List[float]]
) -> List[List[float]]:
    """Compute pairwise cosine similarities for two embedding sets."""
    normalized_queries = [normalize(q) for q in queries]
    normalized_docs = [normalize(d) for d in docs]
    return [[_dot(q, d) for d in normalized_docs] for q in normalized_queries]
