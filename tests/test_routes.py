import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import db, routes
from app.config import Settings
from app.main import app

FIXTURE = Path(__file__).parent / "fixtures" / "sample_snapshot.json"


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for k in ("DO_TOKEN", "SPACES_KEY", "SPACES_SECRET", "SPACES_REGION"):
        monkeypatch.delenv(k, raising=False)


def _setup(tmp_path: Path) -> tuple[Settings, int]:
    """Creates a temp v2 DB with one active account; returns Settings + account id."""
    db_path = tmp_path / "topology.db"
    db.init_db(db_path)
    account = db.create_account(
        db_path,
        name="Test Account",
        token="dop_v1_testtoken_abcdefgh",
        do_account_uuid="test-uuid-1",
        do_account_email="test@example.com",
    )
    db.set_active_account_id(db_path, account["id"])
    settings = Settings(
        active_account_id=account["id"],
        account_name="Test Account",
        do_token="dop_v1_testtoken_abcdefgh",
        spaces_key=None,
        spaces_secret=None,
        spaces_region=None,
        data_dir=tmp_path,
        db_path=db_path,
    )
    return settings, account["id"]


def _bind_db(monkeypatch, db_path: Path) -> None:
    """Points app.config.DB_PATH at a temp DB so get_settings() resolves dynamically."""
    monkeypatch.setattr("app.config.DB_PATH", db_path)


class _FakeDOClient:
    """Stand-in for app.routes.DOClient in tests that exercise token validation."""

    def __init__(self, token: str, *, timeout: float = 15.0) -> None:
        self.token = token

    async def __aenter__(self) -> "_FakeDOClient":
        return self

    async def __aexit__(self, *_exc) -> None:
        return None

    async def get(self, path: str, params: dict | None = None) -> dict:
        if path == "/v2/account":
            return {
                "account": {
                    "uuid": f"uuid-for-{self.token[-6:]}",
                    "email": f"owner-{self.token[-4:]}@example.com",
                }
            }
        return {}


# ---------- snapshot route tests, account-keyed ----------

def test_snapshot_get_returns_graph_and_raw_payload(tmp_path, monkeypatch):
    settings, account_id = _setup(tmp_path)
    payload = json.loads(FIXTURE.read_text())
    snapshot_id = db.insert_snapshot(
        settings.db_path,
        account_id=account_id,
        status="success",
        payload=payload,
        duration_ms=42,
    )
    monkeypatch.setattr(routes, "get_settings", lambda: settings)

    res = TestClient(app).get(f"/api/snapshots/{snapshot_id}")

    assert res.status_code == 200
    data = res.json()
    assert data["snapshot"]["id"] == snapshot_id
    assert data["snapshot"]["account_id"] == account_id
    assert data["snapshot"]["status"] == "success"
    assert data["snapshot"]["duration_ms"] == 42
    assert data["raw"] == payload
    assert "droplet__100" in {n["data"]["id"] for n in data["graph"]["nodes"]}


def test_snapshot_get_404s_for_missing_snapshot(tmp_path, monkeypatch):
    settings, _ = _setup(tmp_path)
    monkeypatch.setattr(routes, "get_settings", lambda: settings)

    res = TestClient(app).get("/api/snapshots/999")

    assert res.status_code == 404
    assert res.json()["detail"] == "Snapshot not found"


# ---------- multi-account route tests ----------

def test_routes_return_409_when_no_active_account(tmp_path, monkeypatch):
    db_path = tmp_path / "topology.db"
    db.init_db(db_path)
    _bind_db(monkeypatch, db_path)

    client = TestClient(app)

    res = client.post("/api/refresh")
    assert res.status_code == 409
    assert res.json()["detail"]["code"] == "no_active_account"

    res = client.put(
        "/api/annotations/droplet__1",
        json={"note": "x", "marked_for_deletion": False},
    )
    assert res.status_code == 409


def test_create_account_validates_and_captures_identity(tmp_path, monkeypatch):
    db_path = tmp_path / "topology.db"
    db.init_db(db_path)
    _bind_db(monkeypatch, db_path)
    monkeypatch.setattr(routes, "DOClient", _FakeDOClient)

    res = TestClient(app).post(
        "/api/accounts",
        json={"name": "Personal", "token": "dop_v1_personal_token_xyz"},
    )

    assert res.status_code == 200, res.text
    body = res.json()
    assert body["name"] == "Personal"
    assert body["do_account_email"].startswith("owner-")
    assert body["do_account_uuid"].startswith("uuid-for-")
    assert body["is_active"] is True
    assert body["token_hint"] == "_xyz"

    accounts = db.list_accounts(db_path)
    assert len(accounts) == 1


def test_create_account_rejects_bad_token_prefix(tmp_path, monkeypatch):
    db_path = tmp_path / "topology.db"
    db.init_db(db_path)
    _bind_db(monkeypatch, db_path)
    monkeypatch.setattr(routes, "DOClient", _FakeDOClient)

    res = TestClient(app).post(
        "/api/accounts", json={"name": "Bad", "token": "not-a-do-token"}
    )
    assert res.status_code == 400


def test_account_switch_isolates_snapshots_and_annotations(tmp_path, monkeypatch):
    db_path = tmp_path / "topology.db"
    db.init_db(db_path)
    _bind_db(monkeypatch, db_path)
    monkeypatch.setattr(routes, "DOClient", _FakeDOClient)

    client = TestClient(app)

    a = client.post("/api/accounts", json={"name": "A", "token": "dop_v1_aaaaaaaa"}).json()
    b = client.post("/api/accounts", json={"name": "B", "token": "dop_v1_bbbbbbbb"}).json()

    db.insert_snapshot(
        db_path,
        account_id=a["id"],
        status="success",
        payload={"droplets": [], "databases": [], "domains": [],
                 "networking": {}, "storage": {}, "compute_extras": {}},
        duration_ms=10,
    )
    client.put(
        "/api/annotations/droplet__100",
        json={"note": "owned by A", "marked_for_deletion": False},
    )

    activate = client.put(f"/api/accounts/{b['id']}/activate")
    assert activate.status_code == 200
    assert activate.json()["active_account_id"] == b["id"]

    assert client.get("/api/snapshots").json()["snapshots"] == []
    assert client.get("/api/annotations").json()["annotations"] == {}

    client.put(f"/api/accounts/{a['id']}/activate")
    assert len(client.get("/api/snapshots").json()["snapshots"]) == 1
    assert "droplet__100" in client.get("/api/annotations").json()["annotations"]


def test_delete_active_account_picks_fallback(tmp_path, monkeypatch):
    db_path = tmp_path / "topology.db"
    db.init_db(db_path)
    _bind_db(monkeypatch, db_path)
    monkeypatch.setattr(routes, "DOClient", _FakeDOClient)

    client = TestClient(app)
    a = client.post("/api/accounts", json={"name": "A", "token": "dop_v1_aaaaaaaa"}).json()
    b = client.post("/api/accounts", json={"name": "B", "token": "dop_v1_bbbbbbbb"}).json()
    assert a["is_active"] is True

    res = client.delete(f"/api/accounts/{a['id']}")
    assert res.status_code == 200
    assert res.json()["active_account_id"] == b["id"]


def test_delete_last_account_clears_active(tmp_path, monkeypatch):
    db_path = tmp_path / "topology.db"
    db.init_db(db_path)
    _bind_db(monkeypatch, db_path)
    monkeypatch.setattr(routes, "DOClient", _FakeDOClient)

    client = TestClient(app)
    a = client.post("/api/accounts", json={"name": "A", "token": "dop_v1_aaaaaaaa"}).json()

    res = client.delete(f"/api/accounts/{a['id']}")
    assert res.status_code == 200
    assert res.json()["active_account_id"] is None
    assert db.get_active_account_id(db_path) is None


def test_health_reports_account_state(tmp_path, monkeypatch):
    db_path = tmp_path / "topology.db"
    db.init_db(db_path)
    _bind_db(monkeypatch, db_path)
    monkeypatch.setattr(routes, "DOClient", _FakeDOClient)

    client = TestClient(app)
    res = client.get("/api/health")
    body = res.json()
    assert body["accounts_count"] == 0
    assert body["active_account_id"] is None
    assert body["token_configured"] is False

    client.post("/api/accounts", json={"name": "A", "token": "dop_v1_aaaaaaaa"})
    body = client.get("/api/health").json()
    assert body["accounts_count"] == 1
    assert body["active_account_id"] is not None
    assert body["account_name"] == "A"
    assert body["token_configured"] is True
