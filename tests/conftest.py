"""Shared pytest fixtures: in-memory database, seeded data and API client."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from iso13485_audit import database as db_module
from iso13485_audit.models.base import Base
from iso13485_audit.seed_data import seed_all


@pytest.fixture()
def engine():
    """A fresh in-memory SQLite engine per test."""
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)


@pytest.fixture()
def session_factory(engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture()
def session(session_factory) -> Iterator[Session]:
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def seeded_session(session) -> Session:
    seed_all(session)
    session.commit()
    return session


@pytest.fixture()
def client(engine, session_factory, monkeypatch) -> Iterator:
    """A FastAPI TestClient backed by the in-memory database."""
    from fastapi.testclient import TestClient

    # Point the app's get_db at our test session factory.
    monkeypatch.setattr(db_module, "_engine", engine)
    monkeypatch.setattr(db_module, "_SessionLocal", session_factory)

    with session_factory() as s:
        seed_all(s)
        s.commit()

    from iso13485_audit.api.app import create_app

    with TestClient(create_app()) as test_client:
        yield test_client
