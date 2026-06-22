"""Thin wrapper over the report generator for use by API and CLI."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from ..reports.generator import generate_report as _generate
from ..schemas.reports import ReportFormat, ReportResponse, ReportType


def generate_report(
    session: Session,
    report_type: ReportType,
    target_id: uuid.UUID,
    fmt: ReportFormat = ReportFormat.HTML,
) -> ReportResponse:
    return _generate(session, report_type, target_id, fmt)
