"""Redis connection factory (async client)."""

import redis.asyncio as redis

from app.core.config import get_settings

settings = get_settings()


def create_redis_client() -> redis.Redis:
    """Create an async Redis client backed by a connection pool.

    The client is lazy: no network call happens until the first command.
    Ownership (lifecycle/close) belongs to the app lifespan.
    """
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        encoding="utf-8",
        decode_responses=True,
        health_check_interval=30,
    )
