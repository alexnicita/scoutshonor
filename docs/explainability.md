# Explainability Notes

This project captures evidence and rationale at each AI touchpoint to satisfy WS-TRUST T-TRUST-04.

## Ranking (semantic search)
- `src/ai/ranker.py` returns `RankedResult` objects with:
  - `score`: cosine similarity between query and document embeddings.
  - `evidence`: snippet of the matched document plus per-item similarity.
  - `explanation`: plain-language description of how the score was derived.
- Preserve document metadata in the evidence payload so downstream callers can trace the source.

## Summarization
- `src/ai/summarizer.py` produces `SummaryResponse` objects with:
  - `summary`: final text returned by the provider.
  - `combined_sources`: list of unique sources that fed the summary.
  - `token_estimate`: coarse word-count estimate to keep budget visibility offline.
- Tests use a mock provider to keep behavior deterministic and auditable.

## Prompt management
- Versioned prompts live under `src/ai/prompts/` with `_vX` suffixes.
- Document which prompt version is in use when shipping changes; keep prior versions for auditability.
