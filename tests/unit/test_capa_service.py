"""Tests for the CAPA workflow state machine."""

from __future__ import annotations

import pytest

from iso13485_audit.models.findings import CAPAStatus, FindingStatus
from iso13485_audit.schemas.audits import AuditCreate
from iso13485_audit.schemas.findings import (
    CAPACreate,
    CAPAUpdate,
    EffectivenessCheck,
    FindingCreate,
)
from iso13485_audit.services import audit_service, capa_service, finding_service
from iso13485_audit.services.capa_service import CAPAServiceError


def _finding(session):
    audit = audit_service.create_audit(session, AuditCreate(title="A"))
    session.flush()
    finding = finding_service.create_finding(
        session,
        FindingCreate(audit_id=audit.id, title="NC", description="Nonconformity found"),
    )
    session.flush()
    return finding


def test_create_capa_generates_number(seeded_session):
    finding = _finding(seeded_session)
    capa = capa_service.create_capa(seeded_session, CAPACreate(finding_id=finding.id))
    assert capa.capa_number.startswith("CAPA-")
    assert finding.status == FindingStatus.CAPA_ASSIGNED


def test_capa_number_increments(seeded_session):
    f1 = _finding(seeded_session)
    f2 = _finding(seeded_session)
    c1 = capa_service.create_capa(seeded_session, CAPACreate(finding_id=f1.id))
    c2 = capa_service.create_capa(seeded_session, CAPACreate(finding_id=f2.id))
    assert c1.capa_number != c2.capa_number


def test_cannot_create_two_capas_for_one_finding(seeded_session):
    finding = _finding(seeded_session)
    capa_service.create_capa(seeded_session, CAPACreate(finding_id=finding.id))
    with pytest.raises(CAPAServiceError):
        capa_service.create_capa(seeded_session, CAPACreate(finding_id=finding.id))


def test_valid_status_progression(seeded_session):
    finding = _finding(seeded_session)
    capa = capa_service.create_capa(seeded_session, CAPACreate(finding_id=finding.id))
    sequence = [
        CAPAStatus.ROOT_CAUSE_ANALYSIS,
        CAPAStatus.ACTION_PLANNED,
        CAPAStatus.ACTION_IN_PROGRESS,
        CAPAStatus.VERIFICATION,
        CAPAStatus.EFFECTIVENESS_CHECK,
        CAPAStatus.CLOSED,
    ]
    for status in sequence:
        capa = capa_service.update_capa(
            seeded_session, capa.id, CAPAUpdate(status=status)
        )
        assert capa.status == status
    assert capa.actual_completion is not None
    assert capa.finding.status == FindingStatus.CLOSED


def test_invalid_transition_rejected(seeded_session):
    finding = _finding(seeded_session)
    capa = capa_service.create_capa(seeded_session, CAPACreate(finding_id=finding.id))
    # Cannot jump straight from INITIATED to CLOSED.
    with pytest.raises(CAPAServiceError):
        capa_service.update_capa(
            seeded_session, capa.id, CAPAUpdate(status=CAPAStatus.CLOSED)
        )


def test_record_effectiveness_closes_capa(seeded_session):
    finding = _finding(seeded_session)
    capa = capa_service.create_capa(seeded_session, CAPACreate(finding_id=finding.id))
    for status in [
        CAPAStatus.ROOT_CAUSE_ANALYSIS,
        CAPAStatus.ACTION_PLANNED,
        CAPAStatus.ACTION_IN_PROGRESS,
        CAPAStatus.VERIFICATION,
        CAPAStatus.EFFECTIVENESS_CHECK,
    ]:
        capa_service.update_capa(seeded_session, capa.id, CAPAUpdate(status=status))
    capa = capa_service.record_effectiveness(
        seeded_session, capa.id, EffectivenessCheck(effectiveness_result="OK", passed=True)
    )
    assert capa.status == CAPAStatus.CLOSED
