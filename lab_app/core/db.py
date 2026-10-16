"""SQLite connection and migrations (01_design/db_schema.md §6)."""
from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

_SCHEMA_DIR = Path(__file__).parent

# Index i holds the script that upgrades user_version i → i+1. Never edit a shipped entry;
# append a new one (ALTER TABLE ...) so existing learning records survive.
MIGRATIONS: list[str] = [
    (_SCHEMA_DIR / "schema_v1.sql").read_text(encoding="utf-8"),
]
SCHEMA_VERSION = len(MIGRATIONS)


def connect(db_path: Path) -> sqlite3.Connection:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # per-connection setting
    return conn


@contextmanager
def transaction(db_path: Path) -> Iterator[sqlite3.Connection]:
    """Commit on success, roll back on error, always close."""
    conn = connect(db_path)
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def init_db(db_path: Path) -> int:
    """Apply pending migrations. Returns the resulting schema version."""
    conn = connect(db_path)
    try:
        version = conn.execute("PRAGMA user_version").fetchone()[0]
        for target in range(version + 1, SCHEMA_VERSION + 1):
            conn.executescript(MIGRATIONS[target - 1])
            conn.execute(f"PRAGMA user_version = {target}")
            conn.commit()
        return conn.execute("PRAGMA user_version").fetchone()[0]
    finally:
        conn.close()
