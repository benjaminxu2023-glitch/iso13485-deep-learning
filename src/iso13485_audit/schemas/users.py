"""Schemas for users."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict

from ..models.users import UserRole


class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    role: UserRole = UserRole.VIEWER


class UserUpdate(BaseModel):
    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
