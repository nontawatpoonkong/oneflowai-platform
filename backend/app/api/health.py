"""Health check endpoints.

  GET /health            -> liveness  (process is up; always 200)
  GET /health/readiness  -> readiness (dependencies reachable; 200 or 503)

Readiness probes PostgreSQL, Redis, and Qdrant and reports each one.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.database.session import get_db
from app.schemas.response import success_response  # used by liveness endpoint

logger = get_logger(__name__)
router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health", summary="Liveness probe")
async def health() -> dict:
    """Fast liveness check. Does not touch dependencies."""
    return success_response(
        data={"status": "alive", "app": settings.APP_NAME, "env": settings.APP_ENV},
        message="Service is alive",
    )


async def _check_database(db: AsyncSession) -> tuple[bool, str]:
    try:
        await db.execute(text("SELECT 1"))
        return True, "ok"
    except Exception as exc:  # noqa: BLE001
        logger.warning("health.database.failed", exc_info=True)
        return False, f"error: {type(exc).__name__}"


async def _check_redis(request: Request) -> tuple[bool, str]:
    try:
        await request.app.state.redis.ping()
        return True, "ok"
    except Exception as exc:  # noqa: BLE001
        logger.warning("health.redis.failed", exc_info=True)
        return False, f"error: {type(exc).__name__}"


async def _check_qdrant(request: Request) -> tuple[bool, str]:
    try:
        await request.app.state.qdrant.get_collections()
        return True, "ok"
    except Exception as exc:  # noqa: BLE001
        logger.warning("health.qdrant.failed", exc_info=True)
        return False, f"error: {type(exc).__name__}"


@router.get("/health/readiness", summary="Readiness probe")
async def readiness(
    request: Request, db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """Check all downstream dependencies. Returns 503 if any is down."""
    db_ok, db_status = await _check_database(db)
    redis_ok, redis_status = await _check_redis(request)
    qdrant_ok, qdrant_status = await _check_qdrant(request)

    checks = {
        "database": db_status,
        "redis": redis_status,
        "qdrant": qdrant_status,
    }
    all_ok = db_ok and redis_ok and qdrant_ok

    body = {
        "success": all_ok,
        "message": "All dependencies healthy"
        if all_ok
        else "One or more dependencies unavailable",
        "data": {
            "status": "ready" if all_ok else "degraded",
            "checks": checks,
        },
        "error": None
        if all_ok
        else {"code": "DEPENDENCY_UNAVAILABLE", "details": checks},
    }
    return JSONResponse(status_code=200 if all_ok else 503, content=body)
