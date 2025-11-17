# Scoutshonor

Minimal, usable FastAPI service with Make targets, scripts, and tests.

## Quickstart

- `make setup` — initialize env (creates `.venv` if Python is present)
- `make run` — start the API server on `:8000`
- `make test` — run tests (pytest if available)
- `make lint` — basic sanity checks (syntax compile)
- `make fmt` — format if a formatter is installed
- `bash scripts/demo-e2e.sh` — run an end-to-end recruiter demo locally

## Layout

- `src/` — production code (`src/app.py` creates the FastAPI app)
- `tests/` — unit tests mirroring `src/`
- `scripts/` — command wrappers used by `Makefile`
- `docs/` and `assets/` — placeholders for docs/static files
- `examples/` — small runnable examples/snippets

## Configuration

- Never commit secrets. Use `.env` locally. See `.env.example`.
- Dependencies are kept minimal; pin versions in `requirements.txt` if added.

## Development

- Code style: 4 spaces for Python, snake_case filenames under `src/` and `tests/`.
- Prefer small, pure functions with clear responsibilities.

## API Overview

- `GET /health` — service health
- `POST /startups/`, `GET /startups/`, `GET /startups/{id}`
- `POST /roles/`, `GET /roles/`, `GET /roles/{id}`
- `POST /candidates/`, `POST /candidates/bulk`, `GET /candidates/`, `GET /candidates/search`, `GET /candidates/{id}`
- `POST /match` — rank candidates for a role
- `POST /outreach` — generate outreach messages
- `POST /sourcing/boolean` — boolean/X-Ray search strings for a role

Auto docs: visit `/docs` once the server is running.

See `examples/recruiter_flow.md` for cURL examples and a step-by-step guide.
See `examples/sourcing.md` for sourcing helpers.

## Contributing

- Use Conventional Commits where practical (e.g., `feat: add parser`).
- Keep commits focused; include rationale when non-obvious.
