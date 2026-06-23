"""Tests for the audit service: lifecycle, checklist generation, summary."""

from __future__ import annotations

import pytest

from iso13485_audit.models.audits import AuditStatus, AuditType, ConformityStatus
from iso13485_audit.schemas.audits import AuditCreate
from iso13485_audit.services import audit_service
from iso13485_audit.services.audit_service import AuditServiceError


def _make_audit(session) -> uuid.UUID:  # noqa: F821
    audit = audit_service.create_audit(
        session, AuditCreate(title="Test Audit", audit_type=AuditType.INTERNAL)
    )
    session.flush()
    return audit.id


def test_create_and_get_audit(seeded_session):
    aid = _make_audit(seeded_session)
    audit = audit_service.get_audit(seeded_session, aid)
    assert audit.title == "Test Audit"
    assert audit.status == AuditStatus.PLANNED


def test_generate_checklist_from_clauses(seeded_session):
    aid = _make_audit(seeded_session)
    checklist = audit_service.generate_checklist(
        seeded_session, aid, clause_numbers=["7.3"]
    )
    assert len(checklist.items) >= 10
    assert all(item.clause_number.startswith("7.3") for item in checklist.items)
    # Generating a checklist moves a planned audit to in_progress.
    audit = audit_service.get_audit(seeded_session, aid)
    assert audit.status == AuditStatus.IN_PROGRESS


def test_generate_checklist_from_template(seeded_session):
    aid = _make_audit(seeded_session)
    checklist = audit_service.generate_checklist(
        seeded_session, aid, template_name="Design Controls Audit"
    )
    assert len(checklist.items) >= 10


def test_generate_checklist_requires_scope(seeded_session):
    aid = _make_audit(seeded_session)
    with pytest.raises(AuditServiceError):
        audit_service.generate_checklist(seeded_session, aid)


def test_audit_summary_counts(seeded_session):
    aid = _make_audit(seeded_session)
    checklist = audit_service.generate_checklist(
        seeded_session, aid, clause_numbers=["7.3.1"]
    )
    items = checklist.items
    audit_service.update_checklist_item(
        seeded_session, items[0].id, conformity_status=ConformityStatus.CONFORMING
    )
    summary = audit_service.compute_audit_summary(seeded_session, aid)
    assert summary.total_items == len(items)
    assert summary.conforming == 1
    assert summary.conformity_rate == 1.0  # only assessed item is conforming


def test_close_audit_sets_end(seeded_session):
    aid = _make_audit(seeded_session)
    audit = audit_service.close_audit(seeded_session, aid)
    assert audit.status == AuditStatus.CLOSED
    assert audit.actual_end is not None
