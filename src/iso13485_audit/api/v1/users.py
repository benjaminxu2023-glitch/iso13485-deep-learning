"""User endpoints (record-keeping; no auth enforcement in the MVP)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import User
from ...schemas.users import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    existing = db.scalar(select(User).where(User.username == data.username))
    if existing is not None:
        raise HTTPException(status_code=409, detail="Username already exists")
    user = User(**data.model_dump())
    db.add(user)
    db.commit()
    return user


@router.get("", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)) -> list[UserResponse]:
    return list(db.scalars(select(User).order_by(User.username)).all())


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)) -> UserResponse:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: uuid.UUID, data: UserUpdate, db: Session = Depends(get_db)
) -> UserResponse:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    return user
