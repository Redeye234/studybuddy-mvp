from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .services.storage import storage_health
from .services.health import db_health, redis_health
from .routers import auth, notes, summaries, focus, memes, subscriptions, jobs
from .db import Base, engine

app = FastAPI(title="StudyBuddy+ API", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.APP_URL, "http://localhost", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/v1", tags=["auth"])
app.include_router(notes.router, prefix="/v1", tags=["notes"])
app.include_router(summaries.router, prefix="/v1", tags=["summaries"])
app.include_router(focus.router, prefix="/v1", tags=["focus"])
app.include_router(memes.router, prefix="/v1", tags=["memes"])
app.include_router(subscriptions.router, prefix="/v1", tags=["subscriptions"])
app.include_router(jobs.router, prefix="/v1", tags=["jobs"])


@app.get("/healthz")
def healthz():
    s = storage_health()
    d = db_health()
    r = redis_health()
    ok = all([s.get("ok"), d.get("ok"), r.get("ok")])
    return {"ok": ok, "storage": s, "db": d, "redis": r}


@app.on_event("startup")
def on_startup():
    # Create tables in dev; replace with Alembic migrations later
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        # In container boot race, DB might not be ready; ignore soft-fail
        pass
