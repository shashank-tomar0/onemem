from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from onemem.home import load_env

load_env()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from onemem.db import get_connection, init_db
    from onemem.pipeline import process_pending_events
    from onemem.providers import get_embedding_model, get_model
    from onemem.startup import announce_embedding_state

    model = get_model()
    embedding_model = get_embedding_model()
    conn = get_connection()
    try:
        init_db(conn)
        announce_embedding_state()
        process_pending_events(conn, model, embedding_model)
    finally:
        conn.close()

    app.state.model = model
    app.state.embedding_model = embedding_model
    yield


app = FastAPI(
    title="oneMEM",
    description="Local structured memory for AI agents",
    lifespan=lifespan,
)

from onemem.api.events import router as events_router

app.include_router(events_router)
