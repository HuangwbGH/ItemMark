import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from module_config import PROJECT_ROOT


ADMIN_DB_PATH = "./data/admin/itemmark_admin.db"


def _db_path() -> str:
    return str(PROJECT_ROOT / ADMIN_DB_PATH)


def connect() -> sqlite3.Connection:
    path = _db_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
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


def start_run(module_key: str, trigger_type: str) -> int:
    init_admin_db()
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO sync_runs(module_key, status, trigger_type, started_at)
            VALUES (?, 'running', ?, ?)
            """,
            (module_key, trigger_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
        return int(cursor.lastrowid)


def finish_run(run_id: int, status: str, stats: Dict[str, Any], error: str = "") -> None:
    with connect() as conn:
        started = conn.execute("SELECT started_at FROM sync_runs WHERE id = ?", (run_id,)).fetchone()
        elapsed = None
        if started and started["started_at"]:
            start_dt = datetime.strptime(started["started_at"], "%Y-%m-%d %H:%M:%S")
            elapsed = (datetime.now() - start_dt).total_seconds()
        conn.execute(
            """
            UPDATE sync_runs
            SET status = ?, finished_at = ?, extracted_count = ?, inserted_count = ?,
                updated_count = ?, failed_count = ?, elapsed_seconds = ?, error_message = ?
            WHERE id = ?
            """,
            (
                status,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                stats.get("extracted", 0),
                stats.get("inserted", 0),
                stats.get("updated", 0),
                stats.get("failed", 0),
                elapsed,
                error,
                run_id,
            ),
        )
        conn.commit()


def running_run(module_key: str) -> Optional[Dict[str, Any]]:
    init_admin_db()
    with connect() as conn:
        row = conn.execute(
            """
            SELECT * FROM sync_runs
            WHERE module_key = ? AND status = 'running'
            ORDER BY id DESC LIMIT 1
            """,
            (module_key,),
        ).fetchone()
        return dict(row) if row else None


def latest_success(module_key: str) -> Optional[Dict[str, Any]]:
    init_admin_db()
    with connect() as conn:
        row = conn.execute(
            """
            SELECT * FROM sync_runs
            WHERE module_key = ? AND status = 'success'
            ORDER BY id DESC LIMIT 1
            """,
            (module_key,),
        ).fetchone()
        return dict(row) if row else None
