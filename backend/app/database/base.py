"""SQLAlchemy declarative base.

This is infrastructure (SQLAlchemy setup), not a domain model. Domain
models live under `app/models/` and will inherit from this Base.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Root declarative base for all ORM models."""

    pass
