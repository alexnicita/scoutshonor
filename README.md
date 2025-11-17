# Scoutshonor

Minimal, usable FastAPI service with Make targets, scripts, and tests.

## Quickstart

- `cp .env.example .env` — start from safe defaults (keep `.env` out of git)
- `make setup` — create `.venv` and install requirements (best-effort offline)
- `make run` — start the API server (defaults to `0.0.0.0:8000`)
- `make test` — run tests (pytest if available; unittest fallback)
- `make lint` / `make fmt` — lightweight lint/format helpers
- `make clean` — remove caches and build artifacts
- `bash scripts/demo-e2e.sh` — run an end-to-end recruiter demo locally
- `bash scripts/gh_fetch_sample.sh` — fetch a small Greenhouse sample (needs `GREENHOUSE_API_KEY`)
- `bash scripts/run_digest.sh` — generate the daily digest and optionally post to Slack

## Layout

- `src/` — production code (`src/app.py` creates the FastAPI app)
- `src/obs/logging.py` — structured logging stub for future observability
- `tests/` — unit tests mirroring `src/`
- `scripts/` — command wrappers used by `Makefile`
- `docs/` and `assets/` — placeholders for docs/static files
- `examples/` — small runnable examples/snippets

## Configuration

- Never commit secrets. Use `.env` locally. See `.env.example`.
- Dependencies are kept minimal; pin versions in `requirements.txt` if added.
- Integrations:
  - Greenhouse/Lever: set `GREENHOUSE_API_KEY` / `LEVER_API_KEY`.
  - Gmail: follow `docs/gmail_setup.md`; tokens live in `.cache/`.
  - Slack: configure bot token and slash commands via `docs/slack_app.yaml`.

## Development

- Tooling entrypoints:
  - `make setup` → `scripts/setup.sh`
  - `make run` → `scripts/run.sh` (uvicorn if present; falls back to python)
  - `make test` → `scripts/test.sh` (pytest or unittest)
  - `make lint` → `scripts/lint.sh` (ruff/syntax + optional shellcheck)
  - `make fmt` → `scripts/fmt.sh` (ruff format/black/autopep8)
  - `make clean` → `scripts/clean.sh`
- Copy `.env.example` to `.env` for local overrides; `.env` is gitignored.
- Code style: 4 spaces for Python, snake_case filenames under `src/` and `tests/`.
- Prefer small, pure functions with clear responsibilities.

## API Overview

- `GET /health` — service health
- `POST /startups/`, `GET /startups/`, `GET /startups/{id}`
- `POST /roles/`, `GET /roles/`, `GET /roles/{id}`
- `POST /candidates/`, `POST /candidates/bulk`, `GET /candidates/`, `GET /candidates/search`, `GET /candidates/{id}`
- `POST /match` — rank candidates for a role
- `POST /outreach` — generate outreach messages
- `POST /descriptions/generate` — generate long job descriptions from minimal inputs
- `POST /sourcing/boolean` — boolean/X-Ray search strings for a role

Auto docs: visit `/docs` once the server is running.

See `examples/recruiter_flow.md` for cURL examples and a step-by-step guide.
See `examples/sourcing.md` for sourcing helpers.
See `examples/descriptions.md` for job description generation.

## Contributing

- Use Conventional Commits where practical (e.g., `feat: add parser`).
- Keep commits focused; include rationale when non-obvious.
