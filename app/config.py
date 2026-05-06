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
    do_token: str | None
    do_token_source: str | None  # "db" | "env" | None
    spaces_key: str | None
    spaces_secret: str | None
    spaces_region: str | None
    data_dir: Path
    db_path: Path


def get_settings() -> Settings:
    # The user-entered token (saved via the Settings UI, stored in SQLite)
    # takes precedence over DO_TOKEN from .env so toggling in the UI always
    # wins. Either source is fine; both are local files on the user's machine.
    db_token = db.get_setting(DB_PATH, "do_token")
    env_token = (os.getenv("DO_TOKEN") or "").strip() or None
    if db_token:
        token, source = db_token, "db"
    elif env_token:
        token, source = env_token, "env"
    else:
        token, source = None, None
    return Settings(
        do_token=token,
        do_token_source=source,
        spaces_key=os.getenv("SPACES_KEY") or None,
        spaces_secret=os.getenv("SPACES_SECRET") or None,
        spaces_region=os.getenv("SPACES_REGION") or None,
        data_dir=DATA_DIR,
        db_path=DB_PATH,
    )
