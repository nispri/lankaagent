"""
LankaAgent — Async Redis Client
"""
import redis.asyncio as aioredis

from app.core.config import settings

redis_client = aioredis.Redis.from_url(
    str(settings.REDIS_URL),
    max_connections=settings.REDIS_MAX_CONNECTIONS,
    decode_responses=settings.REDIS_DECODE_RESPONSES,
)


async def ping_redis() -> bool:
    """Check Redis connectivity"""
    try:
        await redis_client.ping()
        return True
    except Exception:
        return False