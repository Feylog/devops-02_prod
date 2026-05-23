"""FastAPI application entry point.

Composes the URL shortener service from the modules in this package:
- core/config.py: typed settings from env
- db/session.py: SQLAlchemy engine + session factory
- cache/redis_client.py: pooled Redis client
- routers/urls.py: shorten/redirect/stats endpoints
- routers/health.py: /healthz and /readyz

Run locally with:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Run in production via the container's Dockerfile CMD.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.cache.redis_client import redis_client
from app.core.config import settings
from app.db.session import SessionLocal, engine
from app.routers import health, urls

logger = logging.getLogger(__name__)
logging.basicConfig(level=settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup + shutdown hooks bound to the app's lifetime."""

    # --- Startup ---
    logger.info(
        "Starting %s v%s in %s mode",
        settings.app_name,
        settings.app_version,
        settings.environment,
    )

    # Best-effort DB ping at startup. Don't fail startup if it's down;
    # /readyz will reflect the state. The pod stays up; traffic stays away
    # until the DB recovers.
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("MySQL: reachable at startup")
    except Exception as exc:
        logger.warning("MySQL: unreachable at startup (%s) — /readyz will reflect", exc)

    # Same for Redis.
    try:
        redis_client.ping()
        logger.info("Redis: reachable at startup")
    except Exception as exc:
        logger.warning(
            "Redis: unreachable at startup (%s) — falling back to DB on cache miss", exc
        )

    yield  # ← app runs while we're paused here

    # --- Shutdown ---
    logger.info("Shutting down")
    engine.dispose()  # closes all pooled DB connections
    try:
        redis_client.close()
    except Exception:
        pass  # don't crash shutdown on Redis cleanup errors


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# Order matters at runtime but not in include_router calls — FastAPI
# preserves the order within each router. We mount health endpoints
# first because they're operationally important.
app.include_router(health.router, tags=["health"])
app.include_router(urls.router, tags=["urls"])
