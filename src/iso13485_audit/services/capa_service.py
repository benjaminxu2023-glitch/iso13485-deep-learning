"""CAPA workflow engine with an enforced status state machine."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..models import CAPA, CAPAAction, CAPAStatus, Finding, FindingStatus
from ..schemas.findings import (
    CAPAActionCreate,
    CAPAActionUpdate,
    CAPACreate,
    CAPAUpdate,
    EffectivenessCheck,
)

# Allowed forward transitions for the CAPA state machine. CLOSED is terminal.
ALLOWED_TRANSITIONS: dict[CAPAStatus, set[CAPAStatus]] = {
    CAPAStatus.INITIATED: {CAPAStatus.ROOT_CAUSE_ANALYSIS},
    CAPAStatus.ROOT_CAUSE_ANALYSIS: {CAPAStatus.ACTION_PLANNED},
    CAPAStatus.ACTION_PLANNED: {CAPAStatus.ACTION_IN_PROGRESS},
    CAPAStatus.ACTION_IN_PROGRESS: {CAPAStatus.VERIFICATION},
    CAPAStatus.VERIFICATION: {CAPAStatus.EFFECTIVENESS_CHECK},
    CAPAStatus.EFFECTIVENESS_CHECK: {CAPAStatus.CLOSED},
    CAPAStatus.CLOSED: set(),
}


class CAPAServiceError(Exception):
    """Raised for invalid CAPA operations, including illegal status transitions."""


def _generate_capa_number(session: Session) -> str:
    year = datetime.now(timezone.utc).year
    prefix = f"CAPA-{year}-"
    count = session.scalar(
        select(func.count()).select_from(CAPA).where(CAPA.capa_number.like(f"{prefix}%"))
    )
    return f"{prefix}{(count or 0) + 1:03d}"


def create_capa(session: Session, data: CAPACreate) -> CAPA:
    finding = session.get(Finding, data.finding_id)
    if finding is None:
        raise CAPAServiceError(f"Finding {data.finding_id} not found")
    existing = session.scalar(select(CAPA).where(CAPA.finding_id == data.finding_id))
    if existing is not None:
        raise CAPAServiceError(f"Finding {data.finding_id} already has a CAPA")

    capa = CAPA(
        finding_id=data.finding_id,
        capa_number=_generate_capa_number(session),
        capa_type=data.capa_type,
        root_cause=data.root_cause,
        risk_assessment=data.risk_assessment,
        owner_id=data.owner_id,
        target_completion=data.target_completion,
        effectiveness_criteria=data.effectiveness_criteria,
    )
    session.add(capa)
    finding.status = FindingStatus.CAPA_ASSIGNED
    session.flush()
    return capa


def get_capa(session: Session, capa_id: uuid.UUID) -> CAPA | None:
    stmt = (
        select(CAPA).where(CAPA.id == capa_id).options(selectinload(CAPA.actions))
    )
    return session.scalar(stmt)


def list_capas(
    session: Session,
    *,
    status: CAPAStatus | None = None,
) -> list[CAPA]:
    stmt = select(CAPA).order_by(CAPA.created_at.desc()).options(selectinload(CAPA.actions))
    if status is not None:
        stmt = stmt.where(CAPA.status == status)
    return list(session.scalars(stmt).all())


def _validate_transition(current: CAPAStatus, target: CAPAStatus) -> None:
    if target == current:
        return
    if target not in ALLOWED_TRANSITIONS[current]:
        allowed = ", ".join(s.value for s in ALLOWED_TRANSITIONS[current]) or "none"
        raise CAPAServiceError(
            f"Invalid CAPA transition {current.value} -> {target.value}. "
            f"Allowed next: {allowed}"
        )


def update_capa(session: Session, capa_id: uuid.UUID, data: CAPAUpdate) -> CAPA:
    capa = session.get(CAPA, capa_id)
    if capa is None:
        raise CAPAServiceError(f"CAPA {capa_id} not found")

    payload = data.model_dump(exclude_unset=True)
    new_status: CAPAStatus | None = payload.pop("status", None)
    if new_status is not None:
        _validate_transition(capa.status, new_status)
        capa.status = new_status
        if new_status == CAPAStatus.CLOSED:
            capa.actual_completion = capa.actual_completion or datetime.now(timezone.utc)
            if capa.finding is not None:
                capa.finding.status = FindingStatus.CLOSED

    for field, value in payload.items():
        setattr(capa, field, value)
    session.flush()
    return capa


def add_action(session: Session, capa_id: uuid.UUID, data: CAPAActionCreate) -> CAPAAction:
    capa = session.get(CAPA, capa_id)
    if capa is None:
        raise CAPAServiceError(f"CAPA {capa_id} not found")
    action = CAPAAction(
        capa_id=capa_id,
        description=data.description,
        action_type=data.action_type,
        responsible_id=data.responsible_id,
        due_date=data.due_date,
    )
    session.add(action)
    session.flush()
    return action


def update_action(
    session: Session, action_id: uuid.UUID, data: CAPAActionUpdate
) -> CAPAAction:
    action = session.get(CAPAAction, action_id)
    if action is None:
        raise CAPAServiceError(f"CAPA action {action_id} not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(action, field, value)
    session.flush()
    return action


def record_effectiveness(
    session: Session, capa_id: uuid.UUID, data: EffectivenessCheck
) -> CAPA:
    capa = session.get(CAPA, capa_id)
    if capa is None:
        raise CAPAServiceError(f"CAPA {capa_id} not found")
    if capa.status != CAPAStatus.EFFECTIVENESS_CHECK:
        raise CAPAServiceError(
            "Effectiveness can only be recorded while the CAPA is in the "
            "effectiveness_check stage"
        )
    capa.effectiveness_result = data.effectiveness_result
    if data.passed:
        capa.status = CAPAStatus.CLOSED
        capa.actual_completion = datetime.now(timezone.utc)
        if capa.finding is not None:
            capa.finding.status = FindingStatus.CLOSED
    session.flush()
    return capa
