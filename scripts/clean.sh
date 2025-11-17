#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[clean] clearing cache and build artifacts"

targets=(
  ".pytest_cache"
  ".ruff_cache"
  ".mypy_cache"
  ".coverage"
  "htmlcov"
  "build"
  "dist"
)

for target in "${targets[@]}"; do
  if [ -e "$ROOT_DIR/$target" ]; then
    rm -rf "$ROOT_DIR/$target"
  fi
done

find src tests -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
find src tests -type f -name "*.pyc" -delete 2>/dev/null || true

echo "[clean] done"
