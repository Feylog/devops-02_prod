"""Database engine + session factory + FastAPI dependency."""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# One engine per process. The engine owns the connection pool.
engine = create_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    pool_recycle=settings.db_pool_recycle,
    pool_pre_ping=True,  # validate connections before use (recycles dead ones)
    echo=False,  # set True for SQL logging during local debugging
)

# Factory for new Session instances. Sessions are per-request, not shared.
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # accessed attributes survive commit
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yields a session, ensures it's closed.

    Usage in an endpoint:
        def my_endpoint(db: Session = Depends(get_db)):
            db.query(...)

    The try/finally pattern guarantees the session is returned to the
    pool even if the endpoint raises.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
