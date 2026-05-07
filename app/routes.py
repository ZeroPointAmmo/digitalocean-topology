import asyncio
from pathlib import Path
from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app import db, topology
from app.config import get_settings
from app.do_client import DOAPIError, DOClient


class AnnotationBody(BaseModel):
    note: str = Field(default="", max_length=10000)
    marked_for_deletion: bool = False


class TokenBody(BaseModel):
    token: str = Field(min_length=1, max_length=200)

router = APIRouter()
_refresh_lock = asyncio.Lock()

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@router.get("/api/health")
def health() -> dict[str, Any]:
    s = get_settings()
    return {
        "ok": True,
        "token_configured": bool(s.do_token),
        "spaces_configured": bool(s.spaces_key and s.spaces_secret),
    }


@router.get("/api/snapshot/latest")
def snapshot_latest() -> dict[str, Any]:
    s = get_settings()
    snap = db.get_latest_snapshot(s.db_path)
    if snap is None:
        return {"snapshot": None, "graph": {"nodes": [], "edges": []}}
    return _snapshot_response(snap)


@router.get("/api/snapshots/{snapshot_id}")
def snapshot_get(snapshot_id: int) -> dict[str, Any]:
    s = get_settings()
    snap = db.get_snapshot(s.db_path, snapshot_id)
    if snap is None:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return _snapshot_response(snap)


@router.post("/api/refresh")
async def refresh() -> dict[str, Any]:
    s = get_settings()
    if not s.do_token:
        raise HTTPException(
            status_code=400,
            detail="No DigitalOcean API token configured. Open Settings to add one.",
        )
    async with _refresh_lock:
        result = await topology.fetch_snapshot(s.do_token)
        snap_id = db.insert_snapshot(
            s.db_path,
            status=result["status"],
            payload=result["payload"],
            duration_ms=result["duration_ms"],
            error_message=_format_errors(result["errors"]) or None,
        )
    graph = topology.build_graph(result["payload"])
    return {
        "snapshot": {
            "id": snap_id,
            "status": result["status"],
            "duration_ms": result["duration_ms"],
            "errors": result["errors"],
        },
        "graph": graph,
        "raw": result["payload"],
    }


@router.get("/api/snapshots")
def snapshots_list() -> dict[str, Any]:
    s = get_settings()
    return {"snapshots": db.list_snapshot_meta(s.db_path)}


@router.get("/api/annotations")
def annotations_list() -> dict[str, Any]:
    s = get_settings()
    return {"annotations": db.get_all_annotations(s.db_path)}


@router.get("/api/settings")
def settings_get() -> dict[str, Any]:
    s = get_settings()
    if not s.do_token:
        return {"token_configured": False, "source": None, "token_hint": None}
    hint = s.do_token[-4:] if len(s.do_token) >= 8 else "****"
    return {
        "token_configured": True,
        "source": s.do_token_source,
        "token_hint": hint,
    }


@router.put("/api/settings/token")
async def settings_set_token(body: TokenBody) -> dict[str, Any]:
    token = body.token.strip()
    if not token.startswith("dop_v1_"):
        raise HTTPException(
            status_code=400,
            detail="Token doesn't look like a DigitalOcean Personal Access Token (should start with 'dop_v1_').",
        )
    # Validate by making a small authenticated call before persisting.
    try:
        async with DOClient(token, timeout=10.0) as client:
            await client.get("/v2/account")
    except DOAPIError as e:
        if e.status_code == 401:
            raise HTTPException(status_code=401, detail="DigitalOcean rejected this token (401 Unauthorized).")
        raise HTTPException(status_code=400, detail=f"Token validation failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not reach DigitalOcean to validate token: {e}")

    s = get_settings()
    db.set_setting(s.db_path, "do_token", token)
    return {
        "ok": True,
        "token_configured": True,
        "source": "db",
        "token_hint": token[-4:],
    }


@router.delete("/api/settings/token")
def settings_delete_token() -> dict[str, Any]:
    s = get_settings()
    db.delete_setting(s.db_path, "do_token")
    # If DO_TOKEN is still set in the environment, the env value remains as fallback.
    new = get_settings()
    if not new.do_token:
        return {"ok": True, "token_configured": False, "source": None, "token_hint": None}
    return {
        "ok": True,
        "token_configured": True,
        "source": new.do_token_source,
        "token_hint": new.do_token[-4:],
    }


@router.put("/api/annotations/{node_id:path}")
def annotation_upsert(node_id: str, body: AnnotationBody) -> dict[str, Any]:
    s = get_settings()
    if not node_id:
        raise HTTPException(status_code=400, detail="node_id is required")
    return db.upsert_annotation(
        s.db_path,
        node_id,
        note=body.note,
        marked_for_deletion=body.marked_for_deletion,
    )


@router.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


def mount(app: FastAPI) -> None:
    app.include_router(router)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def _format_errors(errors: dict[str, str]) -> str:
    if not errors:
        return ""
    return "; ".join(f"{k}: {v}" for k, v in errors.items())


def _snapshot_response(snap: dict[str, Any]) -> dict[str, Any]:
    graph = topology.build_graph(snap["payload"])
    meta = {k: v for k, v in snap.items() if k != "payload"}
    return {"snapshot": meta, "graph": graph, "raw": snap["payload"]}
