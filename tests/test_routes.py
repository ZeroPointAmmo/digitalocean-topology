import json
from pathlib import Path

from fastapi.testclient import TestClient

from app import db, routes
from app.config import Settings
from app.main import app

FIXTURE = Path(__file__).parent / "fixtures" / "sample_snapshot.json"


def _settings_for(tmp_path: Path) -> Settings:
    return Settings(
        do_token=None,
        do_token_source=None,
        spaces_key=None,
        spaces_secret=None,
        spaces_region=None,
        data_dir=tmp_path,
        db_path=tmp_path / "topology.db",
    )


def test_snapshot_get_returns_graph_and_raw_payload(tmp_path, monkeypatch):
    settings = _settings_for(tmp_path)
    db.init_db(settings.db_path)
    payload = json.loads(FIXTURE.read_text())
    snapshot_id = db.insert_snapshot(
        settings.db_path,
        status="success",
        payload=payload,
        duration_ms=42,
    )
    monkeypatch.setattr(routes, "get_settings", lambda: settings)

    res = TestClient(app).get(f"/api/snapshots/{snapshot_id}")

    assert res.status_code == 200
    data = res.json()
    assert data["snapshot"]["id"] == snapshot_id
    assert data["snapshot"]["status"] == "success"
    assert data["snapshot"]["duration_ms"] == 42
    assert data["raw"] == payload
    assert "droplet__100" in {n["data"]["id"] for n in data["graph"]["nodes"]}


def test_snapshot_get_404s_for_missing_snapshot(tmp_path, monkeypatch):
    settings = _settings_for(tmp_path)
    db.init_db(settings.db_path)
    monkeypatch.setattr(routes, "get_settings", lambda: settings)

    res = TestClient(app).get("/api/snapshots/999")

    assert res.status_code == 404
    assert res.json()["detail"] == "Snapshot not found"
