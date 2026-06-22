"""End-to-end audit workflow: audit -> checklist -> finding -> CAPA -> close -> report."""

from __future__ import annotations

from iso13485_audit.models.audits import ConformityStatus
from iso13485_audit.models.findings import CAPAStatus
from iso13485_audit.schemas.audits import AuditCreate
from iso13485_audit.schemas.findings import (
    CAPACreate,
    CAPAUpdate,
    EffectivenessCheck,
    FindingCreate,
)
from iso13485_audit.schemas.reports import ReportFormat, ReportType
from iso13485_audit.services import (
    audit_service,
    capa_service,
    finding_service,
    report_service,
)


def test_full_audit_lifecycle(seeded_session, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "iso13485_audit.config.Settings.report_output_dir", tmp_path, raising=False
    )

    # 1. Create audit
    audit = audit_service.create_audit(
        seeded_session, AuditCreate(title="E2E Audit")
    )
    seeded_session.flush()

    # 2. Generate checklist for design controls
    checklist = audit_service.generate_checklist(
        seeded_session, audit.id, clause_numbers=["7.3.1"]
    )
    assert checklist.items

    # 3. Assess items - mark one nonconforming
    audit_service.update_checklist_item(
        seeded_session,
        checklist.items[0].id,
        conformity_status=ConformityStatus.NONCONFORMING,
        auditor_notes="No design procedure found",
    )

    # 4. Create a finding
    finding = finding_service.create_finding(
        seeded_session,
        FindingCreate(
            audit_id=audit.id,
            title="No documented design procedure",
            description="Clause 7.3.1 procedure missing.",
            severity="major_nonconformity",
            checklist_item_id=checklist.items[0].id,
        ),
    )
    seeded_session.flush()

    # 5. CAPA through the full state machine
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
        seeded_session,
        capa.id,
        EffectivenessCheck(effectiveness_result="Verified effective", passed=True),
    )
    assert capa.status == CAPAStatus.CLOSED

    # 6. Close the audit
    closed = audit_service.close_audit(seeded_session, audit.id)
    assert closed.status.value == "closed"

    # 7. Generate an HTML report
    seeded_session.commit()
    result = report_service.generate_report(
        seeded_session, ReportType.AUDIT, audit.id, ReportFormat.HTML
    )
    from pathlib import Path

    assert Path(result.file_path).exists()
    content = Path(result.file_path).read_text()
    assert "E2E Audit" in content
