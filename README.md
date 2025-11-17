# AI Tech Exec Recruiter (FastAPI)

An API service that helps automatically recruit technology executives (e.g., CTO, VP Engineering, Head of Platform) to startups. It provides endpoints to register candidates and startups, define roles, score matches, and generate personalized outreach messages.

## Quickstart

### Prerequisites
- Python 3.10+
- `make` (recommended). If unavailable, use scripts in `scripts/`.

### Setup
```bash
make setup
```

### Run the server
```bash
make run
# Visit: http://127.0.0.1:8000/docs
```

### Run tests
```bash
make test
```

### Lint and format
```bash
make lint
make fmt
```

## Project Structure

```
src/
  app.py                 # FastAPI app and router wiring
  models/                # Pydantic domain models
  routers/               # Route handlers (candidates, startups, roles, match, outreach)
  services/              # Matching engine, outreach generator, in-memory repos
tests/
  test_api.py            # API smoke tests
  test_matching.py       # Matching engine tests
scripts/
  setup-env.sh           # Install/initialize environment
  run-server.sh          # Start the API server
  run-tests.sh           # Run tests
  lint.sh                # Lint with ruff
  format.sh              # Format with black
docs/
examples/
  sample_payloads.json   # Example inputs
```

## Design Overview

- Matching engine computes a transparent score with components:
  - Skills overlap, role seniority fit, experience vs. minimum, startup stage alignment, domain overlap, location/timezone, and title signal.
  - Each component contributes to an overall score with human-readable reasons.
- Outreach generator produces channel-ready messages (email/LinkedIn) with tone controls.
- In-memory repositories make the service stateless and easy to demo; swap for a DB later.

## Configuration

- Copy `.env.example` to `.env` and adjust as needed (optional).
- No secrets are required by default; never commit real secrets.

## API Highlights

- `POST /candidates` – Add a candidate profile
- `POST /startups` – Register a startup
- `POST /roles` – Define a role for a startup
- `POST /match` – Rank candidates for a role (by `role_id` or inline payload)
- `POST /outreach` – Generate an outreach subject/body to a candidate for a role
- `GET /health` – Health check

Explore full OpenAPI at `/docs` once the server is running.

## Notes

- This starter avoids external network calls. Replace the simple template-based outreach with your model of choice behind `services/outreach.py`.
- Dependencies are pinned in `requirements.txt`. Python 3.10+ recommended.

