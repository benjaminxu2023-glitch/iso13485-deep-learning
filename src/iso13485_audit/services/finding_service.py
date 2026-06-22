"""Finding CRUD and statistics."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Audit, Finding, FindingSeverity, FindingStatus
from ..schemas.findings import FindingCreate, FindingStatistics, FindingUpdate


class FindingServiceError(Exception):
    """Raised for invalid finding operations."""


def create_finding(session: Session, data: FindingCreate) -> Finding:
    if session.get(Audit, data.audit_id) is None:
        raise FindingServiceError(f"Audit {data.audit_id} not found")
    finding = Finding(
        audit_id=data.audit_id,
        title=data.title,
        description=data.description,
        severity=data.severity,
        checklist_item_id=data.checklist_item_id,
        clause_id=data.clause_id,
        objective_evidence=data.objective_evidence,
        due_date=data.due_date,
    )
    session.add(finding)
    session.flush()
    return finding


def get_finding(session: Session, finding_id: uuid.UUID) -> Finding | None:
    return session.get(Finding, finding_id)


def list_findings(
    session: Session,
    *,
    audit_id: uuid.UUID | None = None,
    severity: FindingSeverity | None = None,
    status: FindingStatus | None = None,
) -> list[Finding]:
    stmt = select(Finding).order_by(Finding.created_at.desc())
    if audit_id is not None:
        stmt = stmt.where(Finding.audit_id == audit_id)
    if severity is not None:
        stmt = stmt.where(Finding.severity == severity)
    if status is not None:
        stmt = stmt.where(Finding.status == status)
    return list(session.scalars(stmt).all())


def update_finding(session: Session, finding_id: uuid.UUID, data: FindingUpdate) -> Finding:
    finding = session.get(Finding, finding_id)
    if finding is None:
        raise FindingServiceError(f"Finding {finding_id} not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(finding, field, value)
    session.flush()
    return finding


def get_statistics(
    session: Session, audit_id: uuid.UUID | None = None
) -> FindingStatistics:
    findings = list_findings(session, audit_id=audit_id)
    by_severity: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for finding in findings:
        by_severity[finding.severity.value] = by_severity.get(finding.severity.value, 0) + 1
        by_status[finding.status.value] = by_status.get(finding.status.value, 0) + 1
    closed = by_status.get(FindingStatus.CLOSED.value, 0)
    return FindingStatistics(
        total=len(findings),
        by_severity=by_severity,
        by_status=by_status,
        open_count=len(findings) - closed,
        closed_count=closed,
    )
