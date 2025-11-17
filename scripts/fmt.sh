#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi

status=0

if command -v ruff >/dev/null 2>&1; then
  echo "[fmt] running ruff format"
  ruff format src tests || status=$?
elif command -v black >/dev/null 2>&1; then
  echo "[fmt] running black"
  black src tests || status=$?
elif command -v autopep8 >/dev/null 2>&1; then
  echo "[fmt] running autopep8"
  autopep8 -ir src tests || status=$?
else
  echo "[fmt] no Python formatter found; skipping (add ruff/black later)"
fi

if command -v shfmt >/dev/null 2>&1; then
  echo "[fmt] running shfmt on scripts"
  shfmt -w scripts/*.sh || status=$?
fi

if [ "$status" -ne 0 ]; then
  exit "$status"
fi

echo "[fmt] done"
