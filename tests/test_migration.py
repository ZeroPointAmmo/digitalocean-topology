"""v1 -> v2 schema migration tests.

The v1 schema was: snapshots/node_annotations without account_id, single token
in settings.do_token. The v2 schema introduces an accounts table and scopes
both child tables to account_id; init_db must migrate existing v1 data into a
seeded "Account 1" without losing snapshots or annotations.
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app import db


_V1_SCHEMA = """
CREATE TABLE snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fetched_at TEXT NOT NULL,
    status TEXT NOT NULL,
    error_message TEXT,
    duration_ms INTEGER,
    payload_json TEXT NOT NULL
);
CREATE INDEX idx_snapshots_fetched_at ON snapshots(fetched_at DESC);

CREATE TABLE node_annotations (
    node_id TEXT PRIMARY KEY,
    note TEXT NOT NULL DEFAULT '',
    marked_for_deletion INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL
);

CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT NOT NULL
);
"""

_NOW = datetime.now(timezone.utc).isoformat()
_EMPTY_PAYLOAD = {
    "droplets": [],
    "databases": [],
    "domains": [],
    "networking": {},
    "storage": {},
    "compute_extras": {},
}


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for k in ("DO_TOKEN", "SPACES_KEY", "SPACES_SECRET", "SPACES_REGION"):
        monkeypatch.delenv(k, raising=False)


def _make_v1_db(
    db_path: Path,
    *,
    db_token: str | None = None,
    snapshot: bool = False,
    annotation_node_id: str | None = None,
) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(_V1_SCHEMA)
        if db_token is not None:
            conn.execute(
                "INSERT INTO settings (key, value, updated_at) VALUES ('do_token', ?, ?)",
                (db_token, _NOW),
            )
        if snapshot:
            conn.execute(
                """
                INSERT INTO snapshots (fetched_at, status, error_message, duration_ms, payload_json)
                VALUES (?, 'success', NULL, 42, ?)
                """,
                (_NOW, json.dumps(_EMPTY_PAYLOAD)),
            )
        if annotation_node_id is not None:
            conn.execute(
                """
                INSERT INTO node_annotations (node_id, note, marked_for_deletion, updated_at)
                VALUES (?, 'legacy note', 0, ?)
                """,
                (annotation_node_id, _NOW),
            )
        conn.commit()
    finally:
        conn.close()


def test_fresh_db_creates_v2_with_no_accounts(tmp_path):
    db_path = tmp_path / "topology.db"
    db.init_db(db_path)
    assert db.get_setting(db_path, "schema_version") == "2"
    assert db.list_accounts(db_path) == []
    assert db.get_active_account_id(db_path) is None


def test_migration_seeds_account_from_db_token(tmp_path):
    db_path = tmp_path / "topology.db"
    _make_v1_db(
        db_path,
        db_token="dop_v1_legacydbtoken",
        snapshot=True,
        annotation_node_id="droplet__100",
    )

    db.init_db(db_path)

    accounts = db.list_accounts(db_path)
    assert len(accounts) == 1
    a = accounts[0]
    assert a["name"] == "Account 1"
    assert a["token"] == "dop_v1_legacydbtoken"
    assert db.get_setting(db_path, "do_token") is None
    assert db.get_active_account_id(db_path) == a["id"]
    snaps = db.list_snapshot_meta(db_path, a["id"])
    assert len(snaps) == 1
    annotations = db.get_all_annotations(db_path, a["id"])
    assert "droplet__100" in annotations
    assert annotations["droplet__100"]["note"] == "legacy note"


def test_migration_seeds_account_from_env_token(tmp_path, monkeypatch):
    monkeypatch.setenv("DO_TOKEN", "dop_v1_envtoken123")
    monkeypatch.setenv("SPACES_KEY", "sk-test")
    monkeypatch.setenv("SPACES_SECRET", "secret-test")
    monkeypatch.setenv("SPACES_REGION", "nyc3")
    db_path = tmp_path / "topology.db"
    _make_v1_db(db_path, snapshot=True)

    db.init_db(db_path)

    accounts = db.list_accounts(db_path)
    assert len(accounts) == 1
    a = accounts[0]
    assert a["name"] == "from .env"
    assert a["token"] == "dop_v1_envtoken123"
    assert a["spaces_key"] == "sk-test"
    assert a["spaces_secret"] == "secret-test"
    assert a["spaces_region"] == "nyc3"


def test_migration_db_token_wins_over_env(tmp_path, monkeypatch):
    monkeypatch.setenv("DO_TOKEN", "dop_v1_envtoken")
    db_path = tmp_path / "topology.db"
    _make_v1_db(db_path, db_token="dop_v1_legacydbtoken")

    db.init_db(db_path)

    accounts = db.list_accounts(db_path)
    assert accounts[0]["token"] == "dop_v1_legacydbtoken"
    assert accounts[0]["name"] == "Account 1"


def test_migration_idempotent(tmp_path):
    db_path = tmp_path / "topology.db"
    _make_v1_db(db_path, db_token="dop_v1_a", snapshot=True)

    db.init_db(db_path)
    db.init_db(db_path)  # second run: no-op

    assert len(db.list_accounts(db_path)) == 1


def test_migration_with_no_token_or_data_does_not_seed(tmp_path):
    db_path = tmp_path / "topology.db"
    _make_v1_db(db_path)  # empty v1, no token, no rows

    db.init_db(db_path)

    assert db.list_accounts(db_path) == []
    assert db.get_active_account_id(db_path) is None


def test_migration_preserves_orphaned_data_with_blank_token(tmp_path):
    """Pathological case: snapshots/annotations exist but no token anywhere."""
    db_path = tmp_path / "topology.db"
    _make_v1_db(db_path, snapshot=True, annotation_node_id="droplet__x")

    db.init_db(db_path)

    accounts = db.list_accounts(db_path)
    assert len(accounts) == 1
    assert accounts[0]["token"] == ""
    assert len(db.list_snapshot_meta(db_path, accounts[0]["id"])) == 1


def test_delete_account_cascades(tmp_path):
    db_path = tmp_path / "topology.db"
    db.init_db(db_path)
    a = db.create_account(db_path, name="A", token="t1")
    db.insert_snapshot(
        db_path, account_id=a["id"], status="success",
        payload=_EMPTY_PAYLOAD, duration_ms=10,
    )
    db.upsert_annotation(
        db_path, a["id"], "droplet__100", note="hi", marked_for_deletion=False,
    )

    assert db.delete_account(db_path, a["id"]) is True
    assert db.list_snapshot_meta(db_path, a["id"]) == []
    assert db.get_all_annotations(db_path, a["id"]) == {}


def test_account_isolation_in_db_layer(tmp_path):
    db_path = tmp_path / "topology.db"
    db.init_db(db_path)
    a = db.create_account(db_path, name="A", token="t1")
    b = db.create_account(db_path, name="B", token="t2")

    db.insert_snapshot(db_path, account_id=a["id"], status="success",
                       payload={"x": "a", **_EMPTY_PAYLOAD}, duration_ms=1)
    db.insert_snapshot(db_path, account_id=b["id"], status="success",
                       payload={"x": "b", **_EMPTY_PAYLOAD}, duration_ms=2)
    db.upsert_annotation(db_path, a["id"], "node-x", note="A note", marked_for_deletion=False)
    db.upsert_annotation(db_path, b["id"], "node-x", note="B note", marked_for_deletion=False)

    assert len(db.list_snapshot_meta(db_path, a["id"])) == 1
    assert len(db.list_snapshot_meta(db_path, b["id"])) == 1
    assert db.get_all_annotations(db_path, a["id"])["node-x"]["note"] == "A note"
    assert db.get_all_annotations(db_path, b["id"])["node-x"]["note"] == "B note"
