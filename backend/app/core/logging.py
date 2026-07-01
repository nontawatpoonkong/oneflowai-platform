"""Logging foundation.

Provides a JSON structured formatter (production) or a human-readable
console formatter (local dev), and wires uvicorn's loggers into the same
handler so all logs share one format.
"""

import json
import logging
import sys
from datetime import UTC, datetime

from app.core.config import get_settings
from app.core.context import get_log_context

# Attributes that live on every LogRecord; anything else passed via
# `logger.info(msg, extra={...})` is treated as structured context.
_RESERVED = frozenset(logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys()) | {
    "message",
    "asctime",
    "taskName",
}

# Context keys injected onto every record by ContextFilter.
_CONTEXT_KEYS = ("request_id", "workspace_id", "user_id")


class ContextFilter(logging.Filter):
    """Attach request-scoped context (request_id/workspace_id/user_id)."""

    def filter(self, record: logging.LogRecord) -> bool:
        for key, value in get_log_context().items():
            setattr(record, key, value)
        return True


class JsonFormatter(logging.Formatter):
    """Serialize log records as single-line JSON (UTF-8, Thai-safe)."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in _RESERVED and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


class ConsoleFormatter(logging.Formatter):
    """Human-readable formatter that appends request context when present."""

    def __init__(self) -> None:
        super().__init__(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        ctx = " ".join(
            f"{key}={getattr(record, key)}"
            for key in _CONTEXT_KEYS
            if getattr(record, key, None) is not None
        )
        return f"{base} | {ctx}" if ctx else base


def setup_logging() -> None:
    """Configure the root logger. Call once at application startup."""
    settings = get_settings()
    level = settings.LOG_LEVEL.upper()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter() if settings.LOG_JSON else ConsoleFormatter())
    handler.addFilter(ContextFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Route uvicorn logs through the root handler for a consistent format.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.propagate = True

    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DB_ECHO else logging.WARNING
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)
