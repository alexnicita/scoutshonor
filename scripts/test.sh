#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi

if command -v pytest >/dev/null 2>&1; then
  echo "[test] running pytest"
  # Use coverage if pytest-cov is available
  if python - <<'PY'
import importlib.util
import sys
sys.exit(0 if importlib.util.find_spec('pytest_cov') else 1)
PY
  then
    exec pytest -q --cov=src --cov-report=term-missing
  else
    exec pytest -q
  fi
fi

if command -v python3 >/dev/null 2>&1; then
  echo "[test] pytest not found; falling back to unittest"
  exec python3 -m unittest discover -s tests -p "test_*.py" -v
fi

echo "[test] python3 not available; cannot run tests"
exit 1
