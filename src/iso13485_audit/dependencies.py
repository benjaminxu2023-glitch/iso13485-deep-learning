"""Shared FastAPI dependency providers."""

from __future__ import annotations

from .config import Settings, get_settings
from .database import get_db

__all__ = ["get_db", "get_settings", "Settings"]
