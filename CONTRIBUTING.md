# Contributing

Thanks for your interest in contributing! This guide covers environment setup, workflow, and expectations so we can ship fast and safely.

## Setup
- Python 3.11+
- Clone, then: `cp .env.example .env`
- Create a venv and install deps: `make setup`
- Run tests: `make test`
- Start the app: `make run`

## Development Workflow
- Branch from `main`: `feat/*`, `fix/*`, `docs/*`.
- Use Conventional Commits (e.g., `feat: add parser`).
- Keep PRs small and focused; include rationale when non-obvious.
- Add/adjust tests for new behavior.

## Linting & Formatting
- Lint: `make lint`
- Format: `make fmt`
- Optional pre-commit hooks: `pre-commit install` (see `.pre-commit-config.yaml`).

## Testing
- Unit tests live in `tests/` mirroring `src/` modules.
- Aim for fast, deterministic tests; prefer fixtures for I/O.
- Coverage: if `pytest-cov` is available, `make test` will report coverage.

## Security
- Do not commit secrets. Use `.env` locally. See `SECURITY.md`.
- Report vulnerabilities privately (GitHub Security Advisories or email alex@nicita.cc).

## Pull Requests
- Include a clear description, screenshots/logs if behavior changes.
- Link issues (e.g., `Closes #123`).
- Request review early for architectural choices; mark as draft if incomplete.

We appreciate your contributions — thank you!
