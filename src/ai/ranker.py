"""Semantic ranker with explainability metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Sequence

from .embeddings import EmbeddingProvider, cosine_similarity


@dataclass
class Document:
    """Plain text document with optional metadata."""

    id: str
    text: str
    metadata: Dict[str, Any] | None = None


@dataclass
class Evidence:
    """Trace data for a ranking decision."""

    snippet: str
    similarity: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RankedResult:
    """Ranked document with explainability metadata."""

    id: str
    score: float
    evidence: List[Evidence]
    explanation: str
    metadata: Dict[str, Any] = field(default_factory=dict)


def rank_documents(
    query: str,
    documents: Sequence[Document],
    embedder: EmbeddingProvider,
    top_k: int | None = None,
) -> List[RankedResult]:
    """Rank documents against a query using cosine similarity."""
    if not documents:
        return []

    query_vec = embedder.embed([query])[0]
    doc_vectors = embedder.embed([doc.text for doc in documents])

    results: List[RankedResult] = []
    for doc, vec in zip(documents, doc_vectors):
        score = cosine_similarity(query_vec, vec)
        snippet = doc.text.strip()
        explanation = (
            "Rank derived from cosine similarity between query and document embeddings."
        )
        result = RankedResult(
            id=doc.id,
            score=round(score, 4),
            evidence=[
                Evidence(
                    snippet=snippet[:200],
                    similarity=score,
                    metadata=doc.metadata or {},
                )
            ],
            explanation=explanation,
            metadata=doc.metadata or {},
        )
        results.append(result)

    results.sort(key=lambda item: item.score, reverse=True)
    if top_k is not None:
        return results[:top_k]
    return results

