"""Schemas for documents, analyses and compliance gaps."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from ..models.documents import DocumentType


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    document_number: str | None = None
    document_type: DocumentType
    version: str | None = None
    file_path: str
    file_hash: str | None = None
    upload_date: datetime


class GapResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    clause_id: uuid.UUID | None = None
    clause_number: str | None = None
    gap_description: str
    severity: str
    confidence: float
    document_excerpt: str | None = None
    recommendation: str | None = None


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    analysis_type: str
    overall_score: float | None = None
    summary: str | None = None
    gaps: list[GapResponse] = []
