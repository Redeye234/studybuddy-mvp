from sqlalchemy import text
from redis import Redis
from ..db import engine
from ..config import settings


def db_health() -> dict:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def redis_health() -> dict:
    try:
        r = Redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        r.ping()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

