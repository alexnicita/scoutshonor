# Prompt Library

Purpose: centralize the prompt variants used for WS-AI tasks (T-AI-01..04) so they stay versioned and reviewable.

## Layout
- `src/ai/prompts/intake_v1.txt` — normalize hiring intake and surface clarifying questions.
- `src/ai/prompts/sourcing_v1.txt` — boolean/X-Ray search helpers and guidance on target companies.
- `src/ai/prompts/outreach_v1.txt` — personalized outreach with tone controls and call to action.
- `src/ai/prompts/screening_v1.txt` — candidate-to-role evaluation with evidence and gaps.

## Versioning
- Keep the `_vX` suffix when updating prompt wording; bump the number for material changes.
- Preserve previous versions for reproducibility; note changes in PR descriptions.
- Align the version used by any orchestration code or tests to avoid silent regressions.

## Usage
- Load prompt files as plain text; substitute dynamic fields (role summary, candidate signals) upstream.
- Avoid injecting secrets or direct identifiers when instantiating prompts—use stable placeholders.
- Keep prompts deterministic for offline tests; mock providers should point to a fixed prompt version.
