import pytest

from src.ai.embeddings import batch_cosine_similarity, cosine_similarity, normalize


def test_cosine_similarity_matches_dot_product():
    a = [1.0, 0.0, 1.0]
    b = [1.0, 0.0, 1.0]
    assert cosine_similarity(a, b) == pytest.approx(1.0)


def test_cosine_similarity_handles_opposing_vectors():
    a = [1.0, 0.0]
    b = [-1.0, 0.0]
    assert cosine_similarity(a, b) == -1.0


def test_batch_cosine_similarity_returns_matrix():
    queries = [[1.0, 0.0], [0.0, 1.0]]
    docs = [[1.0, 0.0], [0.0, 1.0]]
    scores = batch_cosine_similarity(queries, docs)
    assert scores == [[1.0, 0.0], [0.0, 1.0]]


def test_normalize_rejects_zero_vectors():
    try:
        normalize([0.0, 0.0])
    except ValueError as exc:
        assert "zero" in str(exc)
    else:
        raise AssertionError("normalization should reject zero vectors")
