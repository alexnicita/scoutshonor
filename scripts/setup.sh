#!/usr/bin/env bash
set -euo pipefail

# Basic setup script:
# - Creates Python venv if python3 is present
# - Installs requirements.txt if available (best-effort, offline-friendly)

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[setup] initializing project environment..."

PYTHON_BIN="${PYTHON_BIN:-python3}"

if command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  if [ ! -d ".venv" ]; then
    echo "[setup] creating virtualenv at .venv"
    "$PYTHON_BIN" -m venv .venv
  else
    echo "[setup] .venv already exists; reusing"
  fi

  # shellcheck disable=SC1091
  source ".venv/bin/activate"

  if [ -f requirements.txt ]; then
    echo "[setup] installing requirements (best-effort for offline)"
    pip install --upgrade pip setuptools wheel || true
    pip install -r requirements.txt || true
  else
    echo "[setup] no requirements.txt found; skipping installs"
  fi
else
  echo "[setup] ${PYTHON_BIN} not found; skipping virtualenv setup"
fi

echo "[setup] done"
