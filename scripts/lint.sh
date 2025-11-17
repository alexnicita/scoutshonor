#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
shopt -s nullglob

if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi

status=0

if command -v ruff >/dev/null 2>&1; then
  echo "[lint] running ruff"
  ruff check src tests || status=$?
elif command -v python3 >/dev/null 2>&1; then
  echo "[lint] ruff not found; running Python syntax checks"
  python3 - <<'PY' || status=$?
import pathlib
import py_compile
import sys

roots = [pathlib.Path("src"), pathlib.Path("tests")]
py_files = []
for root in roots:
    if root.exists():
        py_files.extend(root.rglob("*.py"))

if not py_files:
    print("[lint] no Python files found")
    raise SystemExit(0)

failed = False
for file in py_files:
    try:
        py_compile.compile(str(file), doraise=True)
    except Exception as exc:  # pragma: no cover - narrow, explicit reporting
        failed = True
        print(f"[lint] failed compiling {file}: {exc}", file=sys.stderr)

if failed:
    raise SystemExit(1)
PY
else
  echo "[lint] python3 not available; skipping Python lint"
fi

shell_scripts=(scripts/*.sh)
if command -v shellcheck >/dev/null 2>&1; then
  if [ "${#shell_scripts[@]}" -gt 0 ]; then
    echo "[lint] running shellcheck"
    shellcheck "${shell_scripts[@]}" || status=$?
  else
    echo "[lint] no shell scripts to lint"
  fi
else
  echo "[lint] shellcheck not installed; skipping shell lint"
fi

if [ "$status" -ne 0 ]; then
  exit "$status"
fi

echo "[lint] done"
