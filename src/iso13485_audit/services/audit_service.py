"""Audit lifecycle, checklist generation and conformity summary."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models import (
    Audit,
    AuditChecklist,
    AuditStatus,
    ChecklistItem,
    ChecklistTemplate,
    ConformityStatus,
    Finding,
)
from ..schemas.audits import AuditCreate, AuditSummary, AuditUpdate
from . import clause_service


class AuditServiceError(Exception):
    """Raised for invalid audit operations."""


def create_audit(session: Session, data: AuditCreate) -> Audit:
    audit = Audit(
        title=data.title,
        audit_type=data.audit_type,
        scope_description=data.scope_description,
        lead_auditor_id=data.lead_auditor_id,
        planned_start=data.planned_start,
        planned_end=data.planned_end,
    )
    session.add(audit)
    session.flush()
    return audit


def get_audit(session: Session, audit_id: uuid.UUID) -> Audit | None:
    stmt = (
        select(Audit)
        .where(Audit.id == audit_id)
        .options(selectinload(Audit.checklists).selectinload(AuditChecklist.items))
    )
    return session.scalar(stmt)


def list_audits(
    session: Session,
    status: AuditStatus | None = None,
    audit_type: str | None = None,
) -> list[Audit]:
    stmt = select(Audit).order_by(Audit.created_at.desc())
    if status is not None:
        stmt = stmt.where(Audit.status == status)
    if audit_type is not None:
        stmt = stmt.where(Audit.audit_type == audit_type)
    return list(session.scalars(stmt).all())


def update_audit(session: Session, audit_id: uuid.UUID, data: AuditUpdate) -> Audit:
    audit = session.get(Audit, audit_id)
    if audit is None:
        raise AuditServiceError(f"Audit {audit_id} not found")
    payload = data.model_dump(exclude_unset=True)

    new_status = payload.get("status")
    if new_status == AuditStatus.IN_PROGRESS and audit.actual_start is None:
        audit.actual_start = datetime.now(timezone.utc)
    if new_status == AuditStatus.CLOSED and audit.actual_end is None:
        audit.actual_end = datetime.now(timezone.utc)

    for field, value in payload.items():
        setattr(audit, field, value)
    session.flush()
    return audit


def close_audit(session: Session, audit_id: uuid.UUID) -> Audit:
    return update_audit(session, audit_id, AuditUpdate(status=AuditStatus.CLOSED))


def generate_checklist(
    session: Session,
    audit_id: uuid.UUID,
    *,
    template_id: uuid.UUID | None = None,
    template_name: str | None = None,
    clause_numbers: list[str] | None = None,
    title: str | None = None,
) -> AuditChecklist:
    """Build a checklist for an audit from a template or an explicit clause list.

    One question is generated per ISO requirement in scope.
    """
    audit = session.get(Audit, audit_id)
    if audit is None:
        raise AuditServiceError(f"Audit {audit_id} not found")

    template: ChecklistTemplate | None = None
    if template_id is not None:
        template = session.get(ChecklistTemplate, template_id)
    elif template_name is not None:
        template = session.scalar(
            select(ChecklistTemplate).where(ChecklistTemplate.name == template_name)
        )

    if template is not None:
        scope = json.loads(template.template_data).get("clauses", [])
        title = title or template.name
    elif clause_numbers:
        scope = clause_numbers
    else:
        raise AuditServiceError(
            "Provide a template_id, template_name or a list of clause_numbers"
        )

    requirements = clause_service.requirements_for_clause_numbers(session, scope)
    if not requirements:
        raise AuditServiceError(f"No requirements found for clauses {scope}")

    checklist = AuditChecklist(
        audit_id=audit.id,
        template_id=template.id if template else None,
        title=title or "Audit Checklist",
    )
    session.add(checklist)
    session.flush()

    requirements.sort(key=lambda r: _sort_key(r.clause.clause_number))
    for order, req in enumerate(requirements):
        session.add(
            ChecklistItem(
                checklist_id=checklist.id,
                requirement_id=req.id,
                clause_number=req.clause.clause_number,
                question=req.requirement_text,
                guidance_notes=req.evidence_guidance,
                sort_order=order,
            )
        )

    if audit.status == AuditStatus.PLANNED:
        audit.status = AuditStatus.IN_PROGRESS
        audit.actual_start = datetime.now(timezone.utc)

    session.flush()
    session.refresh(checklist)
    return checklist


def get_checklist(session: Session, checklist_id: uuid.UUID) -> AuditChecklist | None:
    stmt = (
        select(AuditChecklist)
        .where(AuditChecklist.id == checklist_id)
        .options(selectinload(AuditChecklist.items))
    )
    return session.scalar(stmt)


def update_checklist_item(
    session: Session,
    item_id: uuid.UUID,
    *,
    conformity_status: ConformityStatus | None = None,
    auditor_notes: str | None = None,
    evidence_reference: str | None = None,
) -> ChecklistItem:
    item = session.get(ChecklistItem, item_id)
    if item is None:
        raise AuditServiceError(f"Checklist item {item_id} not found")
    if conformity_status is not None:
        item.conformity_status = conformity_status
    if auditor_notes is not None:
        item.auditor_notes = auditor_notes
    if evidence_reference is not None:
        item.evidence_reference = evidence_reference
    session.flush()
    return item


def compute_audit_summary(session: Session, audit_id: uuid.UUID) -> AuditSummary:
    audit = get_audit(session, audit_id)
    if audit is None:
        raise AuditServiceError(f"Audit {audit_id} not found")

    counts = dict.fromkeys(ConformityStatus, 0)
    total = 0
    for checklist in audit.checklists:
        for item in checklist.items:
            counts[item.conformity_status] += 1
            total += 1

    assessed = total - counts[ConformityStatus.NOT_ASSESSED]
    assessable = (
        counts[ConformityStatus.CONFORMING]
        + counts[ConformityStatus.NONCONFORMING]
        + counts[ConformityStatus.OBSERVATION]
    )
    conformity_rate = (
        counts[ConformityStatus.CONFORMING] / assessable if assessable else 0.0
    )

    findings_count = len(
        session.scalars(select(Finding.id).where(Finding.audit_id == audit_id)).all()
    )

    return AuditSummary(
        audit_id=audit_id,
        total_items=total,
        assessed_items=assessed,
        conforming=counts[ConformityStatus.CONFORMING],
        nonconforming=counts[ConformityStatus.NONCONFORMING],
        observations=counts[ConformityStatus.OBSERVATION],
        not_applicable=counts[ConformityStatus.NOT_APPLICABLE],
        not_assessed=counts[ConformityStatus.NOT_ASSESSED],
        conformity_rate=round(conformity_rate, 4),
        findings_count=findings_count,
    )


def _sort_key(clause_number: str) -> tuple[int, ...]:
    return tuple(int(p) for p in clause_number.split(".") if p.isdigit())
