"""Redis client for cache-aside pattern.

Provides a single connection-pooled Redis client used by routers
for caching short_code -> original_url lookups.
"""

import redis

from app.core.config import settings

# One pool per process.
# Connections are created lazily and reused automatically.
pool: redis.ConnectionPool = redis.ConnectionPool(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=True,  # Return str instead of bytes
    max_connections=50,
)

# Shared Redis client instance.
# Example:
#   from app.cache.redis_client import redis_client
#   redis_client.get("url:abc123")
redis_client: redis.Redis = redis.Redis(connection_pool=pool)
