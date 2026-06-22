"""User and role models (simplified, record-keeping only for the MVP)."""

from __future__ import annotations

import enum

from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, UUIDMixin


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    LEAD_AUDITOR = "lead_auditor"
    AUDITOR = "auditor"
    QUALITY_MANAGER = "quality_manager"
    VIEWER = "viewer"


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    full_name: Mapped[str]
    role: Mapped[UserRole] = mapped_column(default=UserRole.VIEWER)
    is_active: Mapped[bool] = mapped_column(default=True)
    # Optional; the MVP does not enforce authentication.
    hashed_password: Mapped[str | None] = mapped_column(default=None)
