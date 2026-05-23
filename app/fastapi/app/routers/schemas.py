"""Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class ShortenRequest(BaseModel):
    """POST /shorten body."""

    url: HttpUrl


class ShortenResponse(BaseModel):
    """POST /shorten response."""

    short_code: str
    short_url: str
    original_url: str


class StatsResponse(BaseModel):
    """GET /stats/{code} response."""

    model_config = ConfigDict(from_attributes=True)  # allow .from_orm-style population

    short_code: str
    original_url: str
    click_count: int
    created_at: datetime
