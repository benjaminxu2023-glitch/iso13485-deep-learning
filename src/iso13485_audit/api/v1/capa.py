"""CAPA endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import CAPAStatus
from ...schemas.findings import (
    CAPAActionCreate,
    CAPAActionResponse,
    CAPAActionUpdate,
    CAPACreate,
    CAPAResponse,
    CAPAUpdate,
    EffectivenessCheck,
)
from ...services import capa_service
from ...services.capa_service import CAPAServiceError

router = APIRouter(prefix="/capa", tags=["capa"])


@router.post("", response_model=CAPAResponse, status_code=201)
def create_capa(data: CAPACreate, db: Session = Depends(get_db)) -> CAPAResponse:
    try:
        capa = capa_service.create_capa(db, data)
    except CAPAServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    return capa


@router.get("", response_model=list[CAPAResponse])
def list_capas(
    status: CAPAStatus | None = None, db: Session = Depends(get_db)
) -> list[CAPAResponse]:
    return capa_service.list_capas(db, status=status)


@router.get("/{capa_id}", response_model=CAPAResponse)
def get_capa(capa_id: uuid.UUID, db: Session = Depends(get_db)) -> CAPAResponse:
    capa = capa_service.get_capa(db, capa_id)
    if capa is None:
        raise HTTPException(status_code=404, detail="CAPA not found")
    return capa


@router.patch("/{capa_id}", response_model=CAPAResponse)
def update_capa(
    capa_id: uuid.UUID, data: CAPAUpdate, db: Session = Depends(get_db)
) -> CAPAResponse:
    try:
        capa = capa_service.update_capa(db, capa_id, data)
    except CAPAServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    return capa


@router.post("/{capa_id}/actions", response_model=CAPAActionResponse, status_code=201)
def add_action(
    capa_id: uuid.UUID, data: CAPAActionCreate, db: Session = Depends(get_db)
) -> CAPAActionResponse:
    try:
        action = capa_service.add_action(db, capa_id, data)
    except CAPAServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    return action


@router.patch("/{capa_id}/actions/{action_id}", response_model=CAPAActionResponse)
def update_action(
    capa_id: uuid.UUID,
    action_id: uuid.UUID,
    data: CAPAActionUpdate,
    db: Session = Depends(get_db),
) -> CAPAActionResponse:
    try:
        action = capa_service.update_action(db, action_id, data)
    except CAPAServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    db.commit()
    return action


@router.post("/{capa_id}/effectiveness", response_model=CAPAResponse)
def record_effectiveness(
    capa_id: uuid.UUID, data: EffectivenessCheck, db: Session = Depends(get_db)
) -> CAPAResponse:
    try:
        capa = capa_service.record_effectiveness(db, capa_id, data)
    except CAPAServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    return capa
