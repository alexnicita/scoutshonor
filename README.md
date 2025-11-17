# ai-powered recruiting engine

Welcome to Camp Scoutshonor!

## Purpose

- Bold mission: AI-powered recruiting engine that helps small teams do big things — source smarter, match candidates to roles, and send outreach that doesn’t sound like it was whittled by a robot.
- What it does: Ingests roles and candidates, ranks fit, drafts outreach and job descriptions, and generates Boolean/X-Ray strings for sourcing.
- Who it’s for: Startups and talent teams who want a lightweight FastAPI service with sensible scripts, a clean layout, and a trail map you can follow without a compass.
- Scout oath: Keep it simple, test it often, and never commit secrets.

## Quickstart

- `cp .env.example .env`: start from safe defaults (keep `.env` out of git).
- `make setup`: create `.venv` and install requirements (best-effort offline).
- `make run`: start the API server (defaults to `0.0.0.0:8000`).
- `make test`: run tests (pytest if available; unittest fallback).
- `make lint` / `make fmt`: lightweight lint/format helpers.
- `make clean`: remove caches and build artifacts.
- `bash scripts/demo-e2e.sh`: run an end-to-end recruiter demo locally.
- `bash scripts/gh_fetch_sample.sh`: fetch a small Greenhouse sample (needs `GREENHOUSE_API_KEY`).
- `bash scripts/run_digest.sh`: generate the daily digest and optionally post to Slack.

Bring marshmallows; auto docs are at `/docs` once the server is running.

## Map of the Camp (Layout)

- `src/`: production code (`src/app.py` creates the FastAPI app).
- `src/obs/logging.py`: structured logging stub for future observability.
- `tests/`: unit tests mirroring `src/`.
- `scripts/`: command wrappers used by `Makefile`.
- `docs/` and `assets/`: docs and static files.
- `examples/`: runnable snippets for common flows.

## Camp Rules (Configuration)

- Never commit secrets. Use `.env` locally. See `.env.example`.
- Dependencies are minimal; pin versions in `requirements.txt` if added.
- Integrations:
  - Greenhouse/Lever: set `GREENHOUSE_API_KEY` / `LEVER_API_KEY`.
  - Gmail: follow `docs/gmail_setup.md`; tokens live in `.cache/`.
  - Slack: configure bot token and slash commands via `docs/slack_app.yaml`.

## Skills to Earn (Development)

- Entrypoints:
  - `make setup` → `scripts/setup.sh`
  - `make run` → `scripts/run.sh` (uvicorn if present; falls back to python)
  - `make test` → `scripts/test.sh` (pytest or unittest)
  - `make lint` → `scripts/lint.sh` (ruff/syntax + optional shellcheck)
  - `make fmt` → `scripts/fmt.sh` (ruff format/black/autopep8)
  - `make clean` → `scripts/clean.sh`
- Copy `.env.example` to `.env` for local overrides; `.env` is gitignored.
- Code style: 4 spaces for Python; snake_case under `src/` and `tests/`.
- Keep modules small and focused; prefer pure functions.

## Trail Guide (API Overview)

- `GET /health`: service health.
- `POST /startups/`, `GET /startups/`, `GET /startups/{id}`.
- `POST /roles/`, `GET /roles/`, `GET /roles/{id}`.
- `POST /candidates/`, `POST /candidates/bulk`, `GET /candidates/`, `GET /candidates/search`, `GET /candidates/{id}`.
- `POST /match`: rank candidates for a role.
- `POST /outreach`: generate outreach messages.
- `POST /descriptions/generate`: expand minimal inputs into long job descriptions.
- `POST /sourcing/boolean`: create Boolean/X-Ray search strings.

See `examples/recruiter_flow.md` for a step-by-step cURL journey, `examples/sourcing.md` for sourcing helpers, and `examples/descriptions.md` for job description crafting.

## Contributing (Troop Handbook)

- Use Conventional Commits (e.g., `feat: add parser`).
- Keep commits focused; include rationale when non-obvious.
- Open a draft PR early for architectural changes; ask for review before you bushwhack.

See CONTRIBUTING.md for setup and workflow, and CODE_OF_CONDUCT.md for community standards. Security guidance is in SECURITY.md.

## License

Licensed under the MIT License — see LICENSE for details.

Merit badge ideas welcome. Bring snacks, not secrets.
