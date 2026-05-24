from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Required env vars (app refuses to start if missing):
      DATABASE_URL

    All other env vars have defaults suitable for local development.
    """

    # Required
    database_url: str

    # Database connection behavior
    db_pool_size: int = 5
    db_pool_recycle: int = 3600  # recycle connections after 1 hour

    # Redis cache
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_cache_ttl: int = 86400  # 1 day for cached short codes

    # URL shortener behavior
    base_url: str = "http://localhost:8000"
    id_offset: int = 916_132_832  # 62^5: first ID that produces a 6-char base62 code

    # App metadata
    app_name: str = "url-shortener"
    app_version: str = "0.1.0"
    environment: str = "local"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
