"""Audit and checklist endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...schemas.audits import (
    AuditCreate,
    AuditResponse,
    AuditSummary,
    AuditUpdate,
    ChecklistCreate,
    ChecklistItemResponse,
    ChecklistItemUpdate,
    ChecklistResponse,
)
from ...services import audit_service
from ...services.audit_service import AuditServiceError

router = APIRouter(prefix="/audits", tags=["audits"])


@router.post("", response_model=AuditResponse, status_code=201)
def create_audit(data: AuditCreate, db: Session = Depends(get_db)) -> AuditResponse:
    audit = audit_service.create_audit(db, data)
    db.commit()
    return audit


@router.get("", response_model=list[AuditResponse])
def list_audits(db: Session = Depends(get_db)) -> list[AuditResponse]:
    return audit_service.list_audits(db)


@router.get("/{audit_id}", response_model=AuditResponse)
def get_audit(audit_id: uuid.UUID, db: Session = Depends(get_db)) -> AuditResponse:
    audit = audit_service.get_audit(db, audit_id)
    if audit is None:
        raise HTTPException(status_code=404, detail="Audit not found")
    return audit


@router.patch("/{audit_id}", response_model=AuditResponse)
def update_audit(
    audit_id: uuid.UUID, data: AuditUpdate, db: Session = Depends(get_db)
) -> AuditResponse:
    try:
        audit = audit_service.update_audit(db, audit_id, data)
    except AuditServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    db.commit()
    return audit


@router.get("/{audit_id}/summary", response_model=AuditSummary)
def audit_summary(audit_id: uuid.UUID, db: Session = Depends(get_db)) -> AuditSummary:
    try:
        return audit_service.compute_audit_summary(db, audit_id)
    except AuditServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{audit_id}/checklists", response_model=ChecklistResponse, status_code=201)
def create_checklist(
    audit_id: uuid.UUID, data: ChecklistCreate, db: Session = Depends(get_db)
) -> ChecklistResponse:
    try:
        checklist = audit_service.generate_checklist(
            db,
            audit_id,
            template_id=data.template_id,
            template_name=data.template_name,
            clause_numbers=data.clause_numbers,
            title=data.title,
        )
    except AuditServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    return checklist


@router.get("/{audit_id}/checklists/{checklist_id}", response_model=ChecklistResponse)
def get_checklist(
    audit_id: uuid.UUID, checklist_id: uuid.UUID, db: Session = Depends(get_db)
) -> ChecklistResponse:
    checklist = audit_service.get_checklist(db, checklist_id)
    if checklist is None or checklist.audit_id != audit_id:
        raise HTTPException(status_code=404, detail="Checklist not found")
    return checklist


@router.patch(
    "/{audit_id}/checklists/{checklist_id}/items/{item_id}",
    response_model=ChecklistItemResponse,
)
def update_item(
    audit_id: uuid.UUID,
    checklist_id: uuid.UUID,
    item_id: uuid.UUID,
    data: ChecklistItemUpdate,
    db: Session = Depends(get_db),
) -> ChecklistItemResponse:
    try:
        item = audit_service.update_checklist_item(
            db,
            item_id,
            conformity_status=data.conformity_status,
            auditor_notes=data.auditor_notes,
            evidence_reference=data.evidence_reference,
        )
    except AuditServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    db.commit()
    return item
