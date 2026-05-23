"""URL shortener endpoints: shorten, redirect, stats."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.cache.redis_client import redis_client
from app.core.base62 import encode
from app.core.config import settings
from app.db.models import URL
from app.db.session import get_db
from app.routers.schemas import ShortenRequest, ShortenResponse, StatsResponse

router = APIRouter()

CACHE_KEY_PREFIX = "url:"


def _cache_key(short_code: str) -> str:
    return f"{CACHE_KEY_PREFIX}{short_code}"


def _increment_click_count(url_id: int) -> None:
    """Background task: increment click_count for a URL row.

    Runs after the redirect response is already sent to the user, so it
    doesn't add latency to the hot path. Failures here are logged but
    don't affect the user-facing response.
    """
    from app.db.session import SessionLocal  # local import: avoid module-load cycles

    db = SessionLocal()
    try:
        db.execute(
            update(URL).where(URL.id == url_id).values(click_count=URL.click_count + 1)
        )
        db.commit()
    finally:
        db.close()


@router.post("/shorten", response_model=ShortenResponse)
def shorten_url(req: ShortenRequest, db: Session = Depends(get_db)) -> ShortenResponse:
    """Create a short code for the given URL.

    Uses a two-step insert: row is created with a NULL short_code, then
    updated with the base62-encoded id. Both run in one transaction so
    external observers never see the NULL state.
    """
    new_url = URL(original_url=str(req.url))
    db.add(new_url)
    db.flush()  # forces INSERT, populates new_url.id

    new_url.short_code = encode(new_url.id + settings.id_offset)
    db.commit()

    return ShortenResponse(
        short_code=new_url.short_code,
        short_url=f"{settings.base_url}/{new_url.short_code}",
        original_url=new_url.original_url,
    )


@router.get("/stats/{short_code}", response_model=StatsResponse)
def stats(short_code: str, db: Session = Depends(get_db)) -> URL:
    """Return metadata about a shortened URL."""
    row = db.query(URL).filter(URL.short_code == short_code).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    return row


@router.get("/{short_code}")
def redirect(
    short_code: str,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
) -> RedirectResponse:
    """Redirect to the original URL. The hot path.

    Cache-aside: try Redis first. On miss, query the DB, populate the
    cache for next time. The click_count increment runs as a background
    task so it doesn't add latency to the redirect.
    """
    key = _cache_key(short_code)

    # Cache hit path
    cached_url = redis_client.get(key)
    if cached_url is not None:
        # We still want to count this click. But we don't have the row id
        # in the cache. Two options: store id in cache too, or do a tiny
        # SELECT for the id. For now, the simpler path: tiny SELECT.
        # (A more advanced version would cache id alongside the URL.)
        row_id = db.query(URL.id).filter(URL.short_code == short_code).scalar()
        if row_id is not None:
            background.add_task(_increment_click_count, row_id)
        return RedirectResponse(url=cached_url, status_code=status.HTTP_302_FOUND)

    # Cache miss path
    row = db.query(URL).filter(URL.short_code == short_code).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")

    # Populate cache for next time
    redis_client.setex(key, settings.redis_cache_ttl, row.original_url)

    # Count this click in the background
    background.add_task(_increment_click_count, row.id)

    return RedirectResponse(url=row.original_url, status_code=status.HTTP_302_FOUND)
