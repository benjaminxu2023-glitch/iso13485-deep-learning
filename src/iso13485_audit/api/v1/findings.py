"""Finding endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import FindingSeverity, FindingStatus
from ...schemas.findings import (
    FindingCreate,
    FindingResponse,
    FindingStatistics,
    FindingUpdate,
)
from ...services import finding_service
from ...services.finding_service import FindingServiceError

router = APIRouter(prefix="/findings", tags=["findings"])


@router.post("", response_model=FindingResponse, status_code=201)
def create_finding(data: FindingCreate, db: Session = Depends(get_db)) -> FindingResponse:
    try:
        finding = finding_service.create_finding(db, data)
    except FindingServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    return finding


@router.get("", response_model=list[FindingResponse])
def list_findings(
    audit_id: uuid.UUID | None = None,
    severity: FindingSeverity | None = None,
    status: FindingStatus | None = None,
    db: Session = Depends(get_db),
) -> list[FindingResponse]:
    return finding_service.list_findings(
        db, audit_id=audit_id, severity=severity, status=status
    )


@router.get("/statistics", response_model=FindingStatistics)
def finding_statistics(
    audit_id: uuid.UUID | None = None, db: Session = Depends(get_db)
) -> FindingStatistics:
    return finding_service.get_statistics(db, audit_id=audit_id)


@router.get("/{finding_id}", response_model=FindingResponse)
def get_finding(finding_id: uuid.UUID, db: Session = Depends(get_db)) -> FindingResponse:
    finding = finding_service.get_finding(db, finding_id)
    if finding is None:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding


@router.patch("/{finding_id}", response_model=FindingResponse)
def update_finding(
    finding_id: uuid.UUID, data: FindingUpdate, db: Session = Depends(get_db)
) -> FindingResponse:
    try:
        finding = finding_service.update_finding(db, finding_id, data)
    except FindingServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    db.commit()
    return finding
