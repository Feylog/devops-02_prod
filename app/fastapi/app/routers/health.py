"""Liveness and readiness endpoints.

Follows the Kubernetes pattern of separating "process is alive" from
"process is ready to serve traffic":

- /healthz (liveness): is the Python process responsive? No I/O.
  Failure → kubelet kills and restarts the pod.

- /readyz (readiness): are all required dependencies reachable?
  Failure → pod removed from Service endpoints; traffic stops.
  Pod is NOT killed — it stays running until ready again.

We treat MySQL as required (most endpoints need it) and Redis as
optional (the redirect endpoint falls through to the DB on cache miss).
Redis being down returns 200 with a degraded flag, not 503.
"""

from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.cache.redis_client import redis_client
from app.db.session import get_db

router = APIRouter()


@router.get("/healthz")
def healthz() -> dict[str, str]:
    """Liveness: is the process alive? No external I/O.

    If this returns, the HTTP server is functioning. That's all we
    can usefully assert about the process from inside the process.
    """
    return {"status": "ok"}


@router.get("/readyz")
def readyz(db: Session = Depends(get_db)) -> JSONResponse:
    """Readiness: can I actually serve requests?

    Checks MySQL (required) and Redis (optional, degrades gracefully).
    """
    checks: dict[str, Any] = {}
    overall_status = status.HTTP_200_OK

    # MySQL — required. Failure here means we cannot serve.
    try:
        db.execute(text("SELECT 1"))
        checks["mysql"] = "ok"
    except Exception as e:
        checks["mysql"] = f"error: {type(e).__name__}"
        overall_status = status.HTTP_503_SERVICE_UNAVAILABLE

    # Redis — optional. Failure here means degraded performance but
    # we can still serve all endpoints via DB fallback.
    try:
        redis_client.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {type(e).__name__} (degraded, falling back to DB)"
        # Note: we do NOT change overall_status here.

    body = {
        "status": "ok" if overall_status == status.HTTP_200_OK else "not ready",
        "checks": checks,
    }
    return JSONResponse(status_code=overall_status, content=body)
