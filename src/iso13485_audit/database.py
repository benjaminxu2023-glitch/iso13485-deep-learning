"""Database engine, session factory and schema initialisation."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .config import get_settings
from .models.base import Base

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def _build_engine(database_url: str) -> Engine:
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(database_url, connect_args=connect_args, future=True)


def get_engine() -> Engine:
    """Return the process-wide SQLAlchemy engine, creating it on first use."""
    global _engine, _SessionLocal
    if _engine is None:
        settings = get_settings()
        _engine = _build_engine(settings.database_url)
        _SessionLocal = sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    if _SessionLocal is None:
        get_engine()
    assert _SessionLocal is not None
    return _SessionLocal


def init_db() -> None:
    """Create all tables. Importing models registers them on ``Base.metadata``."""
    from . import models  # noqa: F401  (ensures all models are imported)

    Base.metadata.create_all(bind=get_engine())


def drop_db() -> None:
    """Drop all tables."""
    from . import models  # noqa: F401

    Base.metadata.drop_all(bind=get_engine())


@contextmanager
def session_scope() -> Iterator[Session]:
    """Provide a transactional session scope for scripts and the CLI."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Iterator[Session]:
    """FastAPI dependency that yields a session and always closes it."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        session.close()
