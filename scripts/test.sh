#!/usr/bin/env bash
set -euo pipefail

if [ -d .venv ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

if command -v pytest >/dev/null 2>&1; then
  exec pytest -q
fi

if command -v python3 >/dev/null 2>&1; then
  exec python3 -m unittest discover -s tests -p "test_*.py" -v
else
  echo "python3 not found. Please install Python 3 or adjust scripts/test.sh"
  exit 1
fi
