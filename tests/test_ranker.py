from src.ai.ranker import Document, rank_documents


class StaticEmbedder:
    def __init__(self):
        self.vectors = {
            "platform scale": [1.0, 0.0],
            "experience building platforms": [1.0, 0.0],
            "marketing background": [0.0, 1.0],
        }

    def embed(self, texts):
        return [self.vectors[t] for t in texts]


def test_rank_documents_returns_scores_and_evidence():
    embedder = StaticEmbedder()
    documents = [
        Document(id="d1", text="experience building platforms", metadata={"source": "resume"}),
        Document(id="d2", text="marketing background", metadata={"source": "social"}),
    ]

    results = rank_documents("platform scale", documents, embedder)

    assert [r.id for r in results] == ["d1", "d2"]
    assert results[0].score >= results[1].score
    assert results[0].evidence[0].snippet.startswith("experience")
    assert "cosine similarity" in results[0].explanation.lower()
