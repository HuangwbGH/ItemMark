import os
import sqlite3
from typing import Any, Dict, List, Optional

from settings import ADMIN_DB_PATH, rel_path


def connect() -> sqlite3.Connection:
    path = rel_path(ADMIN_DB_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_admin_db() -> None:
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sync_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_key TEXT NOT NULL,
                status TEXT NOT NULL,
                trigger_type TEXT,
                started_at TEXT,
                finished_at TEXT,
                extracted_count INTEGER DEFAULT 0,
                inserted_count INTEGER DEFAULT 0,
                updated_count INTEGER DEFAULT 0,
                failed_count INTEGER DEFAULT 0,
                elapsed_seconds REAL,
                error_message TEXT
            )
            """
        )
        conn.commit()


def latest_run(module_key: str) -> Optional[Dict[str, Any]]:
    init_admin_db()
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM sync_runs WHERE module_key = ? ORDER BY id DESC LIMIT 1",
            (module_key,),
        ).fetchone()
        return dict(row) if row else None


def list_runs(module_key: str, limit: int = 20) -> List[Dict[str, Any]]:
    init_admin_db()
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM sync_runs WHERE module_key = ? ORDER BY id DESC LIMIT ?",
            (module_key, limit),
        ).fetchall()
        return [dict(row) for row in rows]

