#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi

APP_MODULE="${APP_MODULE:-src.app:app}"
APP_ENTRY="${APP_ENTRY:-src.app}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
RELOAD_FLAG="${UVICORN_RELOAD:-true}"

if command -v uvicorn >/dev/null 2>&1; then
  extra_opts=()
  if [ "$RELOAD_FLAG" != "false" ]; then
    extra_opts+=("--reload")
  fi
  exec uvicorn "$APP_MODULE" --host "$HOST" --port "$PORT" "${extra_opts[@]}" "$@"
fi

if command -v python3 >/dev/null 2>&1; then
  echo "[run] uvicorn not found; using python -m $APP_ENTRY"
  exec python3 -m "$APP_ENTRY" "$@"
fi

echo "[run] python3 not available; cannot start app"
exit 1
