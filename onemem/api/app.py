from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from onemem.home import load_env

load_env()


@asynccontextmanager
async def lifespan(app: FastAPI):
    import logging

    from onemem.db import get_connection, init_db
    from onemem.pipeline import process_pending_events
    from onemem.providers import get_embedding_if_available, get_model_if_available
    from onemem.startup import announce_embedding_state

    logger = logging.getLogger(__name__)

    model = get_model_if_available()
    embedding_model = get_embedding_if_available()
    conn = get_connection()
    try:
        init_db(conn)
        announce_embedding_state()
        if model is not None:
            process_pending_events(conn, model, embedding_model)
        else:
            logger.warning("No LLM configured; API started but new memories will remain pending.")
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
