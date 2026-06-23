"""Audit, checklist and checklist-template models."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin


class AuditType(str, enum.Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"
    SUPPLIER = "supplier"
    SURVEILLANCE = "surveillance"
    ML_VALIDATION = "ml_validation"


class AuditStatus(str, enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class ConformityStatus(str, enum.Enum):
    CONFORMING = "conforming"
    NONCONFORMING = "nonconforming"
    OBSERVATION = "observation"
    NOT_ASSESSED = "not_assessed"
    NOT_APPLICABLE = "not_applicable"


class Audit(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "audits"

    title: Mapped[str]
    audit_type: Mapped[AuditType] = mapped_column(default=AuditType.INTERNAL)
    status: Mapped[AuditStatus] = mapped_column(default=AuditStatus.PLANNED)
    scope_description: Mapped[str | None] = mapped_column(Text, default=None)
    lead_auditor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), default=None
    )
    planned_start: Mapped[datetime | None] = mapped_column(default=None)
    planned_end: Mapped[datetime | None] = mapped_column(default=None)
    actual_start: Mapped[datetime | None] = mapped_column(default=None)
    actual_end: Mapped[datetime | None] = mapped_column(default=None)
    clauses_in_scope: Mapped[str | None] = mapped_column(Text, default=None)  # JSON list

    lead_auditor: Mapped[object | None] = relationship("User")
    checklists: Mapped[list[AuditChecklist]] = relationship(
        back_populates="audit", cascade="all, delete-orphan"
    )
    findings: Mapped[list[object]] = relationship(
        "Finding", back_populates="audit", cascade="all, delete-orphan"
    )


class ChecklistTemplate(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "checklist_templates"

    name: Mapped[str] = mapped_column(unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    audit_type: Mapped[AuditType] = mapped_column(default=AuditType.INTERNAL)
    is_default: Mapped[bool] = mapped_column(default=False)
    # JSON: list of {clause_number, question, evidence_required}
    template_data: Mapped[str] = mapped_column(Text, default="[]")


class AuditChecklist(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "audit_checklists"

    audit_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("audits.id"))
    template_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("checklist_templates.id"), default=None
    )
    title: Mapped[str] = mapped_column(default="Audit Checklist")
    completed_at: Mapped[datetime | None] = mapped_column(default=None)

    audit: Mapped[Audit] = relationship(back_populates="checklists")
    template: Mapped[ChecklistTemplate | None] = relationship("ChecklistTemplate")
    items: Mapped[list[ChecklistItem]] = relationship(
        back_populates="checklist", cascade="all, delete-orphan"
    )


class ChecklistItem(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "checklist_items"

    checklist_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("audit_checklists.id"))
    requirement_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("iso_requirements.id"), default=None
    )
    clause_number: Mapped[str | None] = mapped_column(default=None)
    question: Mapped[str] = mapped_column(Text)
    guidance_notes: Mapped[str | None] = mapped_column(Text, default=None)
    conformity_status: Mapped[ConformityStatus] = mapped_column(
        default=ConformityStatus.NOT_ASSESSED
    )
    auditor_notes: Mapped[str | None] = mapped_column(Text, default=None)
    evidence_reference: Mapped[str | None] = mapped_column(default=None)
    sort_order: Mapped[int] = mapped_column(default=0)

    checklist: Mapped[AuditChecklist] = relationship(back_populates="items")
    requirement: Mapped[object | None] = relationship("ISORequirement")
