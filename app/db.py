import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


# ---------- Schema ----------

_SCHEMA_V2 = """
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    token TEXT NOT NULL,
    do_account_uuid TEXT,
    do_account_email TEXT,
    spaces_key TEXT,
    spaces_secret TEXT,
    spaces_region TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_accounts_uuid
    ON accounts(do_account_uuid)
    WHERE do_account_uuid IS NOT NULL;

CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    fetched_at TEXT NOT NULL,
    status TEXT NOT NULL,
    error_message TEXT,
    duration_ms INTEGER,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_snapshots_account_fetched
    ON snapshots(account_id, fetched_at DESC);

CREATE TABLE IF NOT EXISTS node_annotations (
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    node_id TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT '',
    marked_for_deletion INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (account_id, node_id)
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT NOT NULL
);
"""


# ---------- Connection ----------

@contextmanager
def _connect(db_path: Path) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------- init / migration ----------

def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with _connect(db_path) as conn:
        version = _get_schema_version(conn)
        if version == "2":
            return
        if _table_exists(conn, "snapshots") and not _column_exists(conn, "snapshots", "account_id"):
            _migrate_v1_to_v2(conn)
        else:
            conn.executescript(_SCHEMA_V2)
        _set_setting_inner(conn, "schema_version", "2")
        conn.commit()


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone()
    return row is not None


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r["name"] == column for r in rows)


def _get_schema_version(conn: sqlite3.Connection) -> str | None:
    if not _table_exists(conn, "settings"):
        return None
    row = conn.execute(
        "SELECT value FROM settings WHERE key = 'schema_version'"
    ).fetchone()
    return row["value"] if row else None


def _migrate_v1_to_v2(conn: sqlite3.Connection) -> None:
    now = _now()

    conn.execute(
        """
        CREATE TABLE accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            token TEXT NOT NULL,
            do_account_uuid TEXT,
            do_account_email TEXT,
            spaces_key TEXT,
            spaces_secret TEXT,
            spaces_region TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "CREATE UNIQUE INDEX idx_accounts_uuid ON accounts(do_account_uuid) "
        "WHERE do_account_uuid IS NOT NULL"
    )

    db_token = _get_setting_inner(conn, "do_token")
    env_token = (os.getenv("DO_TOKEN") or "").strip() or None
    has_snapshots = conn.execute("SELECT 1 FROM snapshots LIMIT 1").fetchone() is not None
    has_annotations = (
        conn.execute("SELECT 1 FROM node_annotations LIMIT 1").fetchone() is not None
    )

    seed_id: int | None = None
    if db_token or env_token or has_snapshots or has_annotations:
        if db_token:
            token, name = db_token, "Account 1"
        elif env_token:
            token, name = env_token, "from .env"
        else:
            # Pathological: rows exist but no token. Preserve data; the user
            # will need to re-enter a token via the Settings UI.
            token, name = "", "Account 1"
        spaces_key = (os.getenv("SPACES_KEY") or "").strip() or None
        spaces_secret = (os.getenv("SPACES_SECRET") or "").strip() or None
        spaces_region = (os.getenv("SPACES_REGION") or "").strip() or None
        cur = conn.execute(
            """
            INSERT INTO accounts
                (name, token, do_account_uuid, do_account_email,
                 spaces_key, spaces_secret, spaces_region, created_at, updated_at)
            VALUES (?, ?, NULL, NULL, ?, ?, ?, ?, ?)
            """,
            (name, token, spaces_key, spaces_secret, spaces_region, now, now),
        )
        seed_id = int(cur.lastrowid)

    # Rebuild snapshots
    conn.execute(
        """
        CREATE TABLE snapshots_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
            fetched_at TEXT NOT NULL,
            status TEXT NOT NULL,
            error_message TEXT,
            duration_ms INTEGER,
            payload_json TEXT NOT NULL
        )
        """
    )
    if seed_id is not None and has_snapshots:
        conn.execute(
            """
            INSERT INTO snapshots_new
                (id, account_id, fetched_at, status, error_message, duration_ms, payload_json)
            SELECT id, ?, fetched_at, status, error_message, duration_ms, payload_json
            FROM snapshots
            """,
            (seed_id,),
        )
    conn.execute("DROP TABLE snapshots")
    conn.execute("ALTER TABLE snapshots_new RENAME TO snapshots")
    conn.execute(
        "CREATE INDEX idx_snapshots_account_fetched "
        "ON snapshots(account_id, fetched_at DESC)"
    )

    # Rebuild node_annotations
    conn.execute(
        """
        CREATE TABLE node_annotations_new (
            account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
            node_id TEXT NOT NULL,
            note TEXT NOT NULL DEFAULT '',
            marked_for_deletion INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (account_id, node_id)
        )
        """
    )
    if seed_id is not None and has_annotations:
        conn.execute(
            """
            INSERT INTO node_annotations_new
                (account_id, node_id, note, marked_for_deletion, updated_at)
            SELECT ?, node_id, note, marked_for_deletion, updated_at
            FROM node_annotations
            """,
            (seed_id,),
        )
    conn.execute("DROP TABLE node_annotations")
    conn.execute("ALTER TABLE node_annotations_new RENAME TO node_annotations")

    conn.execute("DELETE FROM settings WHERE key = 'do_token'")
    if seed_id is not None:
        _set_setting_inner(conn, "active_account_id", str(seed_id))


# ---------- snapshots (account-scoped) ----------

def insert_snapshot(
    db_path: Path,
    *,
    account_id: int,
    status: str,
    payload: dict[str, Any],
    duration_ms: int,
    error_message: str | None = None,
) -> int:
    fetched_at = _now()
    payload_json = json.dumps(payload)
    with _connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO snapshots
                (account_id, fetched_at, status, error_message, duration_ms, payload_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (account_id, fetched_at, status, error_message, duration_ms, payload_json),
        )
        conn.commit()
        return int(cur.lastrowid)


def get_latest_snapshot(db_path: Path, account_id: int) -> dict[str, Any] | None:
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT id, account_id, fetched_at, status, error_message, duration_ms, payload_json "
            "FROM snapshots WHERE account_id = ? ORDER BY id DESC LIMIT 1",
            (account_id,),
        ).fetchone()
    return _row_to_snapshot(row) if row else None


def get_snapshot(
    db_path: Path, snapshot_id: int, account_id: int
) -> dict[str, Any] | None:
    """Returns the snapshot only if it belongs to the given account."""
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT id, account_id, fetched_at, status, error_message, duration_ms, payload_json "
            "FROM snapshots WHERE id = ? AND account_id = ?",
            (snapshot_id, account_id),
        ).fetchone()
    return _row_to_snapshot(row) if row else None


def list_snapshot_meta(
    db_path: Path, account_id: int, limit: int = 50
) -> list[dict[str, Any]]:
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT id, account_id, fetched_at, status, error_message, duration_ms "
            "FROM snapshots WHERE account_id = ? ORDER BY id DESC LIMIT ?",
            (account_id, limit),
        ).fetchall()
    return [
        {
            "id": r["id"],
            "account_id": r["account_id"],
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
        "account_id": row["account_id"],
        "fetched_at": row["fetched_at"],
        "status": row["status"],
        "error_message": row["error_message"],
        "duration_ms": row["duration_ms"],
        "payload": json.loads(row["payload_json"]),
    }


# ---------- annotations (account-scoped) ----------

def get_all_annotations(
    db_path: Path, account_id: int
) -> dict[str, dict[str, Any]]:
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT account_id, node_id, note, marked_for_deletion, updated_at "
            "FROM node_annotations WHERE account_id = ?",
            (account_id,),
        ).fetchall()
    return {r["node_id"]: _row_to_annotation(r) for r in rows}


def get_annotation(
    db_path: Path, account_id: int, node_id: str
) -> dict[str, Any] | None:
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT account_id, node_id, note, marked_for_deletion, updated_at "
            "FROM node_annotations WHERE account_id = ? AND node_id = ?",
            (account_id, node_id),
        ).fetchone()
    return _row_to_annotation(row) if row else None


def upsert_annotation(
    db_path: Path,
    account_id: int,
    node_id: str,
    *,
    note: str,
    marked_for_deletion: bool,
) -> dict[str, Any]:
    updated_at = _now()
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO node_annotations
                (account_id, node_id, note, marked_for_deletion, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(account_id, node_id) DO UPDATE SET
                note = excluded.note,
                marked_for_deletion = excluded.marked_for_deletion,
                updated_at = excluded.updated_at
            """,
            (account_id, node_id, note, 1 if marked_for_deletion else 0, updated_at),
        )
        conn.commit()
    return {
        "account_id": account_id,
        "node_id": node_id,
        "note": note,
        "marked_for_deletion": marked_for_deletion,
        "updated_at": updated_at,
    }


def _row_to_annotation(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "account_id": row["account_id"],
        "node_id": row["node_id"],
        "note": row["note"] or "",
        "marked_for_deletion": bool(row["marked_for_deletion"]),
        "updated_at": row["updated_at"],
    }


# ---------- accounts ----------

_ACCOUNT_COLUMNS = (
    "id, name, token, do_account_uuid, do_account_email, "
    "spaces_key, spaces_secret, spaces_region, created_at, updated_at"
)


def list_accounts(db_path: Path) -> list[dict[str, Any]]:
    with _connect(db_path) as conn:
        rows = conn.execute(
            f"SELECT {_ACCOUNT_COLUMNS} FROM accounts ORDER BY id"
        ).fetchall()
    return [_row_to_account(r) for r in rows]


def get_account(db_path: Path, account_id: int) -> dict[str, Any] | None:
    with _connect(db_path) as conn:
        row = conn.execute(
            f"SELECT {_ACCOUNT_COLUMNS} FROM accounts WHERE id = ?",
            (account_id,),
        ).fetchone()
    return _row_to_account(row) if row else None


def create_account(
    db_path: Path,
    *,
    name: str,
    token: str,
    do_account_uuid: str | None = None,
    do_account_email: str | None = None,
    spaces_key: str | None = None,
    spaces_secret: str | None = None,
    spaces_region: str | None = None,
) -> dict[str, Any]:
    now = _now()
    with _connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO accounts
                (name, token, do_account_uuid, do_account_email,
                 spaces_key, spaces_secret, spaces_region, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, token, do_account_uuid, do_account_email,
             spaces_key, spaces_secret, spaces_region, now, now),
        )
        account_id = int(cur.lastrowid)
        conn.commit()
        row = conn.execute(
            f"SELECT {_ACCOUNT_COLUMNS} FROM accounts WHERE id = ?",
            (account_id,),
        ).fetchone()
    return _row_to_account(row)


def update_account(
    db_path: Path,
    account_id: int,
    *,
    name: str | None = None,
    token: str | None = None,
    do_account_uuid: str | None = None,
    do_account_email: str | None = None,
    spaces_key: str | None = None,
    spaces_secret: str | None = None,
    spaces_region: str | None = None,
    update_spaces: bool = False,
) -> dict[str, Any] | None:
    """Updates only fields explicitly passed. Set update_spaces=True to write
    the three spaces_* columns (including clearing them by passing None)."""
    fields: list[str] = []
    values: list[Any] = []
    if name is not None:
        fields.append("name = ?")
        values.append(name)
    if token is not None:
        fields.append("token = ?")
        values.append(token)
    if do_account_uuid is not None:
        fields.append("do_account_uuid = ?")
        values.append(do_account_uuid)
    if do_account_email is not None:
        fields.append("do_account_email = ?")
        values.append(do_account_email)
    if update_spaces:
        fields.append("spaces_key = ?")
        values.append(spaces_key)
        fields.append("spaces_secret = ?")
        values.append(spaces_secret)
        fields.append("spaces_region = ?")
        values.append(spaces_region)
    if not fields:
        return get_account(db_path, account_id)
    fields.append("updated_at = ?")
    values.append(_now())
    values.append(account_id)
    with _connect(db_path) as conn:
        conn.execute(
            f"UPDATE accounts SET {', '.join(fields)} WHERE id = ?",
            values,
        )
        conn.commit()
    return get_account(db_path, account_id)


def delete_account(db_path: Path, account_id: int) -> bool:
    with _connect(db_path) as conn:
        cur = conn.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
        conn.commit()
        return cur.rowcount > 0


def _row_to_account(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "token": row["token"],
        "do_account_uuid": row["do_account_uuid"],
        "do_account_email": row["do_account_email"],
        "spaces_key": row["spaces_key"],
        "spaces_secret": row["spaces_secret"],
        "spaces_region": row["spaces_region"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def get_active_account_id(db_path: Path) -> int | None:
    raw = get_setting(db_path, "active_account_id")
    if raw is None:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def set_active_account_id(db_path: Path, account_id: int) -> None:
    set_setting(db_path, "active_account_id", str(account_id))


def clear_active_account(db_path: Path) -> None:
    delete_setting(db_path, "active_account_id")


# ---------- key-value settings ----------

def get_setting(db_path: Path, key: str) -> str | None:
    try:
        with _connect(db_path) as conn:
            return _get_setting_inner(conn, key)
    except sqlite3.OperationalError:
        return None


def set_setting(db_path: Path, key: str, value: str) -> None:
    with _connect(db_path) as conn:
        _set_setting_inner(conn, key, value)
        conn.commit()


def delete_setting(db_path: Path, key: str) -> None:
    with _connect(db_path) as conn:
        conn.execute("DELETE FROM settings WHERE key = ?", (key,))
        conn.commit()


def _get_setting_inner(conn: sqlite3.Connection, key: str) -> str | None:
    if not _table_exists(conn, "settings"):
        return None
    row = conn.execute(
        "SELECT value FROM settings WHERE key = ?", (key,)
    ).fetchone()
    return row["value"] if row else None


def _set_setting_inner(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        """
        INSERT INTO settings (key, value, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET
            value = excluded.value,
            updated_at = excluded.updated_at
        """,
        (key, value, _now()),
    )
