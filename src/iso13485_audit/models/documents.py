"""Document, analysis and compliance-gap models."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin


class DocumentType(str, enum.Enum):
    QMS_MANUAL = "qms_manual"
    SOP = "sop"
    WORK_INSTRUCTION = "work_instruction"
    FORM = "form"
    RECORD = "record"
    POLICY = "policy"
    DHF = "design_history_file"
    DMR = "device_master_record"
    DHR = "device_history_record"
    RISK_MANAGEMENT = "risk_management"
    OTHER = "other"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Document(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "documents"

    title: Mapped[str]
    document_number: Mapped[str | None] = mapped_column(default=None)
    document_type: Mapped[DocumentType] = mapped_column(default=DocumentType.OTHER)
    version: Mapped[str | None] = mapped_column(default=None)
    file_path: Mapped[str]
    file_hash: Mapped[str | None] = mapped_column(default=None)  # SHA-256
    content_text: Mapped[str | None] = mapped_column(Text, default=None)
    upload_date: Mapped[datetime] = mapped_column(default=_utcnow)

    analyses: Mapped[list[DocumentAnalysis]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class DocumentAnalysis(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "document_analyses"

    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id"))
    analysis_type: Mapped[str] = mapped_column(default="gap_detection")
    overall_score: Mapped[float | None] = mapped_column(default=None)  # 0..1 coverage
    summary: Mapped[str | None] = mapped_column(Text, default=None)
    raw_results: Mapped[str | None] = mapped_column(Text, default=None)  # JSON

    document: Mapped[Document] = relationship(back_populates="analyses")
    gaps: Mapped[list[ComplianceGap]] = relationship(
        back_populates="analysis", cascade="all, delete-orphan"
    )


class ComplianceGap(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "compliance_gaps"

    analysis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("document_analyses.id"))
    clause_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("iso_clauses.id"), default=None
    )
    clause_number: Mapped[str | None] = mapped_column(default=None)
    gap_description: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(default="medium")  # high | medium | low
    confidence: Mapped[float] = mapped_column(default=0.0)
    document_excerpt: Mapped[str | None] = mapped_column(Text, default=None)
    recommendation: Mapped[str | None] = mapped_column(Text, default=None)

    analysis: Mapped[DocumentAnalysis] = relationship(back_populates="gaps")
    clause: Mapped[object | None] = relationship("ISOClause")
