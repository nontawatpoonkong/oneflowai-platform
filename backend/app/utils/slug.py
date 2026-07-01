"""Slug helpers: normalization and uniqueness-validated generation."""

import re
import secrets
from collections.abc import Awaitable, Callable

_SLUG_STRIP = re.compile(r"[^a-z0-9]+")
_DEFAULT_MAX_ATTEMPTS = 5


def slugify(value: str) -> str:
    """Lowercase, ASCII-ish slug. Falls back to 'workspace' when empty."""
    slug = _SLUG_STRIP.sub("-", value.strip().lower()).strip("-")
    return slug or "workspace"


def unique_suffix(length: int = 6) -> str:
    """Short URL-safe random suffix for guaranteeing slug uniqueness."""
    return secrets.token_hex(length // 2 + 1)[:length]


async def generate_unique_slug(
    name: str,
    exists: Callable[[str], Awaitable[bool]],
    *,
    max_attempts: int = _DEFAULT_MAX_ATTEMPTS,
) -> str:
    """Generate a slug from ``name`` that passes the ``exists`` check.

    ``exists`` is an async predicate (typically a repository lookup) returning
    True when a slug is already taken. The base slug is tried first, then a
    random suffix is appended until a free slug is found. A DB-level unique
    constraint remains the final guarantee against races.
    """
    base = slugify(name)
    candidate = base
    for _ in range(max_attempts):
        if not await exists(candidate):
            return candidate
        candidate = f"{base}-{unique_suffix()}"
    # Extremely unlikely; final fallback with a longer suffix.
    return f"{base}-{unique_suffix(12)}"
