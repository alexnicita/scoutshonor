#!/usr/bin/env bash
set -euo pipefail

source .venv/bin/activate
exec uvicorn src.app:app --reload --port ${PORT:-8000}

