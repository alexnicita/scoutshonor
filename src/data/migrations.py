"""Migration runner for the lightweight SQLite store.

Purpose:
    Apply ordered `.sql` files from the repository `migrations/` directory and
    track which versions have been executed in `schema_migrations`.
Dependencies:
    Standard library only (sqlite3, pathlib).
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
from typing import Iterable, Set


DEFAULT_MIGRATIONS_DIR = Path(__file__).resolve().parent.parent.parent / "migrations"


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _ensure_migrations_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()


def _applied_versions(conn: sqlite3.Connection) -> Set[str]:
    _ensure_migrations_table(conn)
    rows = conn.execute("SELECT version FROM schema_migrations").fetchall()
    return {row["version"] for row in rows}


def _load_migrations(migrations_dir: Path) -> Iterable[Path]:
    return sorted(migrations_dir.glob("*.sql"))


def apply_migrations(
    db_path: str | None,
    migrations_dir: Path | None = None,
    *,
    connection: sqlite3.Connection | None = None,
) -> None:
    """Apply pending migrations to the SQLite database at `db_path`.

    If an open SQLite `connection` is provided the migrations run there; otherwise
    the runner opens and owns its own connection.
    """
    mig_dir = migrations_dir or DEFAULT_MIGRATIONS_DIR
    if connection is None and db_path is None:
        raise ValueError("db_path is required when a connection is not provided")

    conn = connection or _connect(db_path or "")
    seen = _applied_versions(conn)

    for migration in _load_migrations(mig_dir):
        version = migration.name
        if version in seen:
            continue

        sql = migration.read_text(encoding="utf-8")
        conn.executescript(sql)
        conn.execute(
            "INSERT INTO schema_migrations(version) VALUES (?)", (version,)
        )
        conn.commit()

    if connection is None:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply local SQLite migrations.")
    parser.add_argument(
        "--db-path",
        default=str(Path("data") / "app.db"),
        help="Where to create/use the SQLite database.",
    )
    parser.add_argument(
        "--migrations-dir",
        default=str(DEFAULT_MIGRATIONS_DIR),
        help="Directory containing *.sql migration files.",
    )
    args = parser.parse_args()
    apply_migrations(args.db_path, Path(args.migrations_dir))


if __name__ == "__main__":
    main()
