#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB_PATH="${DB_PATH:-${ROOT}/data/app.db}"

mkdir -p "$(dirname "${DB_PATH}")"
python -m src.data.migrations --db-path "${DB_PATH}" --migrations-dir "${ROOT}/migrations"
echo "Migrations applied to ${DB_PATH}"
