#!/usr/bin/env bash
set -euo pipefail

# Basic setup script:
# - Creates Python venv if python3 is present
# - Installs requirements.txt if available (best-effort, offline-friendly)

echo "[setup] initializing project environment..."

if command -v python3 >/dev/null 2>&1; then
  if [ ! -d .venv ]; then
    echo "[setup] creating virtualenv at .venv"
    python3 -m venv .venv
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate

  if [ -f requirements.txt ]; then
    echo "[setup] installing requirements (may be skipped if offline)"
    # Continue even if install fails due to offline environment
    pip install --upgrade pip setuptools wheel || true
    pip install -r requirements.txt || true
  else
    echo "[setup] no requirements.txt found; skipping installs"
  fi
else
  echo "[setup] python3 not found; skipping virtualenv setup"
fi

echo "[setup] done"

