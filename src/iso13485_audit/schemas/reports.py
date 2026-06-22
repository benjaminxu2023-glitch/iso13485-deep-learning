"""Schemas for report generation."""

from __future__ import annotations

import enum
import uuid

from pydantic import BaseModel


class ReportType(str, enum.Enum):
    AUDIT = "audit"
    CAPA = "capa"
    GAP_ANALYSIS = "gap_analysis"
    ML_VALIDATION = "ml_validation"


class ReportFormat(str, enum.Enum):
    HTML = "html"
    PDF = "pdf"


class ReportGenerateRequest(BaseModel):
    report_type: ReportType
    target_id: uuid.UUID
    format: ReportFormat = ReportFormat.HTML


class ReportResponse(BaseModel):
    report_type: ReportType
    format: ReportFormat
    file_path: str
    filename: str
