import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from app import db

load_dotenv()

DATA_DIR = Path(os.getenv("DATA_DIR", "/app/data"))
DB_PATH = DATA_DIR / "topology.db"


@dataclass(frozen=True)
class Settings:
    active_account_id: int | None
    account_name: str | None
    do_token: str | None
    spaces_key: str | None
    spaces_secret: str | None
    spaces_region: str | None
    data_dir: Path
    db_path: Path


def get_settings() -> Settings:
    """Resolves the *active* account into a flat Settings view used by routes.

    Token, spaces creds, and account name come from the active accounts row.
    The env vars `DO_TOKEN` / `SPACES_*` are only consulted by the v1->v2
    migration in `db.init_db`; once an account row exists they are ignored.
    """
    active_id = db.get_active_account_id(DB_PATH)
    account = db.get_account(DB_PATH, active_id) if active_id is not None else None
    if account is None:
        return Settings(
            active_account_id=None,
            account_name=None,
            do_token=None,
            spaces_key=None,
            spaces_secret=None,
            spaces_region=None,
            data_dir=DATA_DIR,
            db_path=DB_PATH,
        )
    token = (account["token"] or "").strip() or None
    return Settings(
        active_account_id=int(account["id"]),
        account_name=account["name"],
        do_token=token,
        spaces_key=account["spaces_key"] or None,
        spaces_secret=account["spaces_secret"] or None,
        spaces_region=account["spaces_region"] or None,
        data_dir=DATA_DIR,
        db_path=DB_PATH,
    )
