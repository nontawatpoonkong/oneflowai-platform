"""Qdrant connection factory (async client).

Sprint 1 only establishes connectivity for health checks. No collections
or vector operations are created here.
"""

from qdrant_client import AsyncQdrantClient

from app.core.config import get_settings

settings = get_settings()


def create_qdrant_client() -> AsyncQdrantClient:
    """Create an async Qdrant client. Lifecycle is owned by the lifespan."""
    return AsyncQdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
        api_key=settings.QDRANT_API_KEY,
        https=False,
    )
