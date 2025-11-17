from src.ai.summarizer import Summarizer, SummaryChunk


class MockProvider:
    def __init__(self, response: str):
        self.response = response
        self.last_prompt: str | None = None
        self.name = "mock-provider"

    def complete(self, prompt: str) -> str:
        self.last_prompt = prompt
        return self.response


def test_summarizer_returns_schema_and_tracks_prompt():
    provider = MockProvider("Condensed summary.")
    chunks = [
        SummaryChunk(
            id="c1", text="Senior engineer with platform leadership.", source="resume"
        ),
        SummaryChunk(
            id="c2", text="Interested in remote-first startups.", source="intake"
        ),
    ]
    summarizer = Summarizer(provider)

    result = summarizer.summarize(chunks, instruction="Focus on leadership impact.")

    assert result.summary == "Condensed summary."
    assert result.provider == "mock-provider"
    assert set(result.combined_sources) == {"resume", "intake"}
    assert result.token_estimate > 0
    assert provider.last_prompt is not None
    assert "leadership" in provider.last_prompt
    assert "c1" in provider.last_prompt


def test_summarizer_requires_content():
    provider = MockProvider("n/a")
    summarizer = Summarizer(provider)
    try:
        summarizer.summarize([])
    except ValueError as exc:
        assert "no content" in str(exc)
    else:
        raise AssertionError("expected summarizer to reject empty input")
