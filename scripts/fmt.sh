#!/usr/bin/env bash
set -euo pipefail

# Placeholder formatter script; extend once a formatter is chosen.

if command -v black >/dev/null 2>&1; then
  echo "[fmt] running black"
  black src tests
elif command -v autopep8 >/dev/null 2>&1; then
  echo "[fmt] running autopep8"
  autopep8 -ir src tests
else
  echo "[fmt] no Python formatter found; skipping (add black/ruff later)"
fi

echo "[fmt] done"

