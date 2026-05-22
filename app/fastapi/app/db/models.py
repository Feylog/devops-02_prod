"""SQLAlchemy ORM models for the URL shortener."""

from datetime import datetime
from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all ORM models in the project.

    All models inherit from this. Alembic will discover tables by
    importing Base.metadata.
    """

    pass


class URL(Base):
    """A shortened URL.

    Lifecycle:
        1. Row inserted with original_url and NULL short_code.
        2. Caller computes short_code = base62(id + ID_OFFSET) and UPDATEs.
        3. Row is now serveable. The two statements run in one transaction
           so external observers never see the NULL state.
    """

    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    short_code: Mapped[str | None] = mapped_column(
        String(16),
        unique=True,
        index=True,
        nullable=True,
    )

    original_url: Mapped[str] = mapped_column(
        String(2048),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    click_count: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        server_default="0",
    )

    def __repr__(self) -> str:
        return f"<URL id={self.id} short_code={self.short_code!r}>"
