#!/usr/bin/env bash
set -euo pipefail

# Wrapper to run the primary app

if [ -d .venv ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

if command -v python3 >/dev/null 2>&1; then
  exec python3 -m src.app "$@"
else
  echo "python3 not found. Please install Python 3 or adjust scripts/run.sh"
  exit 1
fi

