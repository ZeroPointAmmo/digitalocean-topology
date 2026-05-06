from fastapi import FastAPI

from app import db, routes
from app.config import get_settings

app = FastAPI(title="DigitalOcean Topology Visualizer")


@app.on_event("startup")
def on_startup() -> None:
    s = get_settings()
    db.init_db(s.db_path)


routes.mount(app)
