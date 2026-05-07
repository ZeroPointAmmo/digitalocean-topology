import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


SCHEMA = """
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fetched_at TEXT NOT NULL,
    status TEXT NOT NULL,
    error_message TEXT,
    duration_ms INTEGER,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_snapshots_fetched_at ON snapshots(fetched_at DESC);

CREATE TABLE IF NOT EXISTS node_annotations (
    node_id TEXT PRIMARY KEY,
    note TEXT NOT NULL DEFAULT '',
    marked_for_deletion INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT NOT NULL
);
"""


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with _connect(db_path) as conn:
        conn.executescript(SCHEMA)
        conn.commit()


@contextmanager
def _connect(db_path: Path) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def insert_snapshot(
    db_path: Path,
    *,
    status: str,
    payload: dict[str, Any],
    duration_ms: int,
    error_message: str | None = None,
) -> int:
    fetched_at = datetime.now(timezone.utc).isoformat()
    payload_json = json.dumps(payload)
    with _connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO snapshots (fetched_at, status, error_message, duration_ms, payload_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (fetched_at, status, error_message, duration_ms, payload_json),
        )
        conn.commit()
        return int(cur.lastrowid)


def get_latest_snapshot(db_path: Path) -> dict[str, Any] | None:
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT id, fetched_at, status, error_message, duration_ms, payload_json "
            "FROM snapshots ORDER BY id DESC LIMIT 1"
        ).fetchone()
    if row is None:
        return None
    return _row_to_snapshot(row)


def get_snapshot(db_path: Path, snapshot_id: int) -> dict[str, Any] | None:
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT id, fetched_at, status, error_message, duration_ms, payload_json "
            "FROM snapshots WHERE id = ?",
            (snapshot_id,),
        ).fetchone()
    if row is None:
        return None
    return _row_to_snapshot(row)


def list_snapshot_meta(db_path: Path, limit: int = 50) -> list[dict[str, Any]]:
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT id, fetched_at, status, error_message, duration_ms "
            "FROM snapshots ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [
        {
            "id": r["id"],
            "fetched_at": r["fetched_at"],
            "status": r["status"],
            "error_message": r["error_message"],
            "duration_ms": r["duration_ms"],
        }
        for r in rows
    ]


def _row_to_snapshot(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "fetched_at": row["fetched_at"],
        "status": row["status"],
        "error_message": row["error_message"],
        "duration_ms": row["duration_ms"],
        "payload": json.loads(row["payload_json"]),
    }


def get_all_annotations(db_path: Path) -> dict[str, dict[str, Any]]:
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT node_id, note, marked_for_deletion, updated_at FROM node_annotations"
        ).fetchall()
    return {r["node_id"]: _row_to_annotation(r) for r in rows}


def get_annotation(db_path: Path, node_id: str) -> dict[str, Any] | None:
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT node_id, note, marked_for_deletion, updated_at "
            "FROM node_annotations WHERE node_id = ?",
            (node_id,),
        ).fetchone()
    return _row_to_annotation(row) if row else None


def upsert_annotation(
    db_path: Path,
    node_id: str,
    *,
    note: str,
    marked_for_deletion: bool,
) -> dict[str, Any]:
    updated_at = datetime.now(timezone.utc).isoformat()
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO node_annotations (node_id, note, marked_for_deletion, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(node_id) DO UPDATE SET
                note = excluded.note,
                marked_for_deletion = excluded.marked_for_deletion,
                updated_at = excluded.updated_at
            """,
            (node_id, note, 1 if marked_for_deletion else 0, updated_at),
        )
        conn.commit()
    return {
        "node_id": node_id,
        "note": note,
        "marked_for_deletion": marked_for_deletion,
        "updated_at": updated_at,
    }


def _row_to_annotation(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "node_id": row["node_id"],
        "note": row["note"] or "",
        "marked_for_deletion": bool(row["marked_for_deletion"]),
        "updated_at": row["updated_at"],
    }


# ----- key-value settings (used for the user-entered DO API token) -----

def get_setting(db_path: Path, key: str) -> str | None:
    try:
        with _connect(db_path) as conn:
            row = conn.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            ).fetchone()
    except sqlite3.OperationalError:
        # Database file or table doesn't exist yet (first run before init)
        return None
    return row["value"] if row else None


def set_setting(db_path: Path, key: str, value: str) -> None:
    updated_at = datetime.now(timezone.utc).isoformat()
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO settings (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
            """,
            (key, value, updated_at),
        )
        conn.commit()


def delete_setting(db_path: Path, key: str) -> None:
    with _connect(db_path) as conn:
        conn.execute("DELETE FROM settings WHERE key = ?", (key,))
        conn.commit()
