"""Report generation orchestration: gather data via services, render, persist."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from .. import __version__
from ..config import get_settings
from ..models import CAPA, Document
from ..schemas.reports import ReportFormat, ReportResponse, ReportType
from ..services import audit_service, document_service, finding_service
from . import html_renderer, pdf_renderer

_TEMPLATES = {
    ReportType.AUDIT: "audit_report.html",
    ReportType.CAPA: "capa_report.html",
    ReportType.GAP_ANALYSIS: "gap_analysis.html",
    ReportType.ML_VALIDATION: "ml_validation_report.html",
}


class ReportError(Exception):
    """Raised when a report cannot be generated."""


def generate_report(
    session: Session,
    report_type: ReportType,
    target_id: uuid.UUID,
    fmt: ReportFormat = ReportFormat.HTML,
) -> ReportResponse:
    context = _gather(session, report_type, target_id)
    context["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    context["system_version"] = __version__

    html = html_renderer.render(_TEMPLATES[report_type], context)

    settings = get_settings()
    settings.ensure_dirs()
    stem = f"{report_type.value}_{target_id.hex[:8]}_{datetime.now(timezone.utc):%Y%m%d%H%M%S}"

    if fmt == ReportFormat.PDF:
        filename = f"{stem}.pdf"
        out_path = settings.report_output_dir / filename
        pdf_renderer.html_to_pdf(html, str(out_path))
    else:
        filename = f"{stem}.html"
        out_path = settings.report_output_dir / filename
        Path(out_path).write_text(html, encoding="utf-8")

    return ReportResponse(
        report_type=report_type,
        format=fmt,
        file_path=str(out_path),
        filename=filename,
    )


def _gather(session: Session, report_type: ReportType, target_id: uuid.UUID) -> dict:
    if report_type == ReportType.AUDIT:
        return _gather_audit(session, target_id)
    if report_type == ReportType.CAPA:
        return _gather_capa(session, target_id)
    if report_type == ReportType.GAP_ANALYSIS:
        return _gather_gap(session, target_id)
    if report_type == ReportType.ML_VALIDATION:
        return _gather_ml(session, target_id)
    raise ReportError(f"Unknown report type {report_type}")


def _gather_audit(session: Session, audit_id: uuid.UUID) -> dict:
    audit = audit_service.get_audit(session, audit_id)
    if audit is None:
        raise ReportError(f"Audit {audit_id} not found")
    summary = audit_service.compute_audit_summary(session, audit_id)
    findings = finding_service.list_findings(session, audit_id=audit_id)
    return {"audit": audit, "summary": summary, "findings": findings}


def _gather_capa(session: Session, capa_id: uuid.UUID) -> dict:
    capa = session.get(CAPA, capa_id)
    if capa is None:
        raise ReportError(f"CAPA {capa_id} not found")
    return {"capa": capa, "finding": capa.finding, "actions": capa.actions}


def _gather_gap(session: Session, document_id: uuid.UUID) -> dict:
    document = session.get(Document, document_id)
    if document is None:
        raise ReportError(f"Document {document_id} not found")
    analysis = document_service.get_latest_analysis(session, document_id)
    if analysis is None:
        raise ReportError(f"Document {document_id} has no analysis; run analyze first")
    return {"document": document, "analysis": analysis, "gaps": analysis.gaps}


def _gather_ml(session: Session, model_id: uuid.UUID) -> dict:
    from ..services import ml_audit_service

    model = ml_audit_service.get_model(session, model_id)
    if model is None:
        raise ReportError(f"ML model {model_id} not found")
    lifecycle = ml_audit_service.get_lifecycle_status(session, model_id)
    metrics = json.loads(model.performance_metrics) if model.performance_metrics else {}
    return {
        "model": model,
        "datasets": model.datasets,
        "validations": model.validations,
        "bias_assessments": model.bias_assessments,
        "lifecycle": lifecycle,
        "metrics": metrics,
    }
