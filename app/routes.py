import asyncio
import sqlite3
from pathlib import Path
from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app import db, topology
from app.config import Settings, get_settings
from app.do_client import DOAPIError, DOClient


class AnnotationBody(BaseModel):
    note: str = Field(default="", max_length=10000)
    marked_for_deletion: bool = False


class CreateAccountBody(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    token: str = Field(min_length=1, max_length=200)
    spaces_key: str | None = Field(default=None, max_length=500)
    spaces_secret: str | None = Field(default=None, max_length=500)
    spaces_region: str | None = Field(default=None, max_length=50)


class UpdateAccountBody(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    token: str | None = Field(default=None, min_length=1, max_length=200)
    spaces_key: str | None = Field(default=None, max_length=500)
    spaces_secret: str | None = Field(default=None, max_length=500)
    spaces_region: str | None = Field(default=None, max_length=50)


router = APIRouter()
_refresh_lock = asyncio.Lock()

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


# ---------- helpers ----------

def _require_active(s: Settings) -> int:
    if s.active_account_id is None:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "no_active_account",
                "message": "No DigitalOcean account is active. Open Accounts in Settings.",
            },
        )
    return s.active_account_id


async def _validate_token_and_capture(token: str) -> tuple[str | None, str | None]:
    """Validates a DO PAT against /v2/account; returns (uuid, email) on success."""
    if not token.startswith("dop_v1_"):
        raise HTTPException(
            status_code=400,
            detail="Token doesn't look like a DigitalOcean Personal Access Token (should start with 'dop_v1_').",
        )
    try:
        async with DOClient(token, timeout=10.0) as client:
            data = await client.get("/v2/account")
    except DOAPIError as e:
        if e.status_code == 401:
            raise HTTPException(status_code=401, detail="DigitalOcean rejected this token (401 Unauthorized).")
        raise HTTPException(status_code=400, detail=f"Token validation failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not reach DigitalOcean to validate token: {e}")
    account_data = data.get("account") if isinstance(data, dict) else None
    if not isinstance(account_data, dict):
        return None, None
    return account_data.get("uuid"), account_data.get("email")


def _public_account(acct: dict[str, Any], active_id: int | None) -> dict[str, Any]:
    token = acct.get("token") or ""
    if not token:
        token_hint = None
    elif len(token) >= 8:
        token_hint = token[-4:]
    else:
        token_hint = "****"
    return {
        "id": acct["id"],
        "name": acct["name"],
        "do_account_uuid": acct.get("do_account_uuid"),
        "do_account_email": acct.get("do_account_email"),
        "token_hint": token_hint,
        "is_active": active_id is not None and active_id == acct["id"],
        "spaces_configured": bool(acct.get("spaces_key") and acct.get("spaces_secret")),
        "created_at": acct["created_at"],
        "updated_at": acct["updated_at"],
    }


# ---------- health & bootstrap ----------

@router.get("/api/health")
def health() -> dict[str, Any]:
    s = get_settings()
    accounts_count = len(db.list_accounts(s.db_path))
    return {
        "ok": True,
        "active_account_id": s.active_account_id,
        "account_name": s.account_name,
        "accounts_count": accounts_count,
        "token_configured": bool(s.do_token),
        "spaces_configured": bool(s.spaces_key and s.spaces_secret),
    }


@router.get("/api/settings")
def settings_get() -> dict[str, Any]:
    s = get_settings()
    return {
        "active_account_id": s.active_account_id,
        "accounts_count": len(db.list_accounts(s.db_path)),
    }


# ---------- snapshots ----------

@router.get("/api/snapshot/latest")
def snapshot_latest() -> dict[str, Any]:
    s = get_settings()
    if s.active_account_id is None:
        return {"snapshot": None, "graph": {"nodes": [], "edges": []}}
    snap = db.get_latest_snapshot(s.db_path, s.active_account_id)
    if snap is None:
        return {"snapshot": None, "graph": {"nodes": [], "edges": []}}
    return _snapshot_response(snap)


@router.get("/api/snapshots/{snapshot_id}")
def snapshot_get(snapshot_id: int) -> dict[str, Any]:
    s = get_settings()
    account_id = _require_active(s)
    snap = db.get_snapshot(s.db_path, snapshot_id, account_id)
    if snap is None:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return _snapshot_response(snap)


@router.post("/api/refresh")
async def refresh() -> dict[str, Any]:
    s = get_settings()
    account_id = _require_active(s)
    if not s.do_token:
        raise HTTPException(
            status_code=400,
            detail="Active account has no token configured. Edit it in Settings.",
        )
    async with _refresh_lock:
        result = await topology.fetch_snapshot(s.do_token)
        snap_id = db.insert_snapshot(
            s.db_path,
            account_id=account_id,
            status=result["status"],
            payload=result["payload"],
            duration_ms=result["duration_ms"],
            error_message=_format_errors(result["errors"]) or None,
        )
    graph = topology.build_graph(result["payload"])
    return {
        "snapshot": {
            "id": snap_id,
            "account_id": account_id,
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
    if s.active_account_id is None:
        return {"snapshots": []}
    return {"snapshots": db.list_snapshot_meta(s.db_path, s.active_account_id)}


# ---------- annotations ----------

@router.get("/api/annotations")
def annotations_list() -> dict[str, Any]:
    s = get_settings()
    if s.active_account_id is None:
        return {"annotations": {}}
    return {"annotations": db.get_all_annotations(s.db_path, s.active_account_id)}


@router.put("/api/annotations/{node_id:path}")
def annotation_upsert(node_id: str, body: AnnotationBody) -> dict[str, Any]:
    s = get_settings()
    account_id = _require_active(s)
    if not node_id:
        raise HTTPException(status_code=400, detail="node_id is required")
    return db.upsert_annotation(
        s.db_path,
        account_id,
        node_id,
        note=body.note,
        marked_for_deletion=body.marked_for_deletion,
    )


# ---------- accounts ----------

@router.get("/api/accounts")
def accounts_list() -> dict[str, Any]:
    s = get_settings()
    accounts = db.list_accounts(s.db_path)
    return {
        "accounts": [_public_account(a, s.active_account_id) for a in accounts],
        "active_account_id": s.active_account_id,
    }


@router.post("/api/accounts")
async def account_create(body: CreateAccountBody) -> dict[str, Any]:
    s = get_settings()
    token = body.token.strip()
    uuid, email = await _validate_token_and_capture(token)
    try:
        account = db.create_account(
            s.db_path,
            name=body.name.strip(),
            token=token,
            do_account_uuid=uuid,
            do_account_email=email,
            spaces_key=(body.spaces_key or None),
            spaces_secret=(body.spaces_secret or None),
            spaces_region=(body.spaces_region or None),
        )
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="An account with this DigitalOcean uuid already exists.",
        )
    if db.get_active_account_id(s.db_path) is None:
        db.set_active_account_id(s.db_path, account["id"])
    return _public_account(account, db.get_active_account_id(s.db_path))


@router.patch("/api/accounts/{account_id}")
async def account_update(account_id: int, body: UpdateAccountBody) -> dict[str, Any]:
    s = get_settings()
    existing = db.get_account(s.db_path, account_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Account not found")

    fields_set = body.model_fields_set
    update_spaces = bool(
        {"spaces_key", "spaces_secret", "spaces_region"} & fields_set
    )

    new_token: str | None = None
    new_uuid: str | None = None
    new_email: str | None = None
    if "token" in fields_set and body.token is not None:
        new_token = body.token.strip()
        new_uuid, new_email = await _validate_token_and_capture(new_token)

    try:
        account = db.update_account(
            s.db_path,
            account_id,
            name=(body.name.strip() if body.name is not None else None),
            token=new_token,
            do_account_uuid=new_uuid,
            do_account_email=new_email,
            spaces_key=(body.spaces_key or None),
            spaces_secret=(body.spaces_secret or None),
            spaces_region=(body.spaces_region or None),
            update_spaces=update_spaces,
        )
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Another account already uses this DigitalOcean uuid.",
        )
    return _public_account(account, db.get_active_account_id(s.db_path))


@router.delete("/api/accounts/{account_id}")
def account_delete(account_id: int) -> dict[str, Any]:
    s = get_settings()
    existed = db.delete_account(s.db_path, account_id)
    if not existed:
        raise HTTPException(status_code=404, detail="Account not found")
    if s.active_account_id == account_id:
        remaining = db.list_accounts(s.db_path)
        if remaining:
            db.set_active_account_id(s.db_path, remaining[0]["id"])
        else:
            db.clear_active_account(s.db_path)
    return {"ok": True, "active_account_id": db.get_active_account_id(s.db_path)}


@router.put("/api/accounts/{account_id}/activate")
def account_activate(account_id: int) -> dict[str, Any]:
    s = get_settings()
    target = db.get_account(s.db_path, account_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Account not found")
    db.set_active_account_id(s.db_path, account_id)
    return {"ok": True, "active_account_id": account_id}


# ---------- index + mount ----------

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
