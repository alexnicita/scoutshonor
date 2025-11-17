#!/usr/bin/env bash
set -euo pipefail

# Lightweight, dependency-free sanity checks

echo "[lint] compiling Python files to check syntax"
if command -v python3 >/dev/null 2>&1; then
  python3 -m py_compile $(find src -name "*.py") || exit 1
else
  echo "python3 not found; skipping Python lint"
fi

echo "[lint] shellcheck not configured; consider adding it later"
echo "[lint] done"

