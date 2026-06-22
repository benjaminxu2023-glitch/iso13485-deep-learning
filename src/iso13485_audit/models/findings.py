"""Finding, CAPA, CAPA action and evidence models."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin


class FindingSeverity(str, enum.Enum):
    MAJOR_NC = "major_nonconformity"
    MINOR_NC = "minor_nonconformity"
    OBSERVATION = "observation"
    OPPORTUNITY = "opportunity_for_improvement"


class FindingStatus(str, enum.Enum):
    OPEN = "open"
    CAPA_ASSIGNED = "capa_assigned"
    VERIFICATION_PENDING = "verification_pending"
    CLOSED = "closed"


class CAPAType(str, enum.Enum):
    CORRECTIVE = "corrective"
    PREVENTIVE = "preventive"
    BOTH = "corrective_and_preventive"


class CAPAStatus(str, enum.Enum):
    INITIATED = "initiated"
    ROOT_CAUSE_ANALYSIS = "root_cause_analysis"
    ACTION_PLANNED = "action_planned"
    ACTION_IN_PROGRESS = "action_in_progress"
    VERIFICATION = "verification"
    EFFECTIVENESS_CHECK = "effectiveness_check"
    CLOSED = "closed"


class Finding(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "findings"

    audit_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("audits.id"))
    checklist_item_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("checklist_items.id"), default=None
    )
    clause_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("iso_clauses.id"), default=None
    )
    title: Mapped[str]
    description: Mapped[str] = mapped_column(Text)
    objective_evidence: Mapped[str | None] = mapped_column(Text, default=None)
    severity: Mapped[FindingSeverity] = mapped_column(default=FindingSeverity.MINOR_NC)
    status: Mapped[FindingStatus] = mapped_column(default=FindingStatus.OPEN)
    due_date: Mapped[datetime | None] = mapped_column(default=None)

    audit: Mapped[object] = relationship("Audit", back_populates="findings")
    clause: Mapped[object | None] = relationship("ISOClause")
    capa: Mapped[CAPA | None] = relationship(
        back_populates="finding", uselist=False, cascade="all, delete-orphan"
    )
    evidence_items: Mapped[list[Evidence]] = relationship(
        back_populates="finding", cascade="all, delete-orphan"
    )


class CAPA(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "capas"

    finding_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("findings.id"), unique=True)
    capa_number: Mapped[str] = mapped_column(unique=True, index=True)  # CAPA-YYYY-NNN
    capa_type: Mapped[CAPAType] = mapped_column(default=CAPAType.CORRECTIVE)
    status: Mapped[CAPAStatus] = mapped_column(default=CAPAStatus.INITIATED)
    root_cause: Mapped[str | None] = mapped_column(Text, default=None)
    risk_assessment: Mapped[str | None] = mapped_column(Text, default=None)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), default=None)
    target_completion: Mapped[datetime | None] = mapped_column(default=None)
    actual_completion: Mapped[datetime | None] = mapped_column(default=None)
    effectiveness_criteria: Mapped[str | None] = mapped_column(Text, default=None)
    effectiveness_result: Mapped[str | None] = mapped_column(Text, default=None)

    finding: Mapped[Finding] = relationship(back_populates="capa")
    owner: Mapped[object | None] = relationship("User")
    actions: Mapped[list[CAPAAction]] = relationship(
        back_populates="capa", cascade="all, delete-orphan"
    )


class CAPAAction(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "capa_actions"

    capa_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("capas.id"))
    description: Mapped[str] = mapped_column(Text)
    action_type: Mapped[str] = mapped_column(default="corrective")
    responsible_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), default=None
    )
    due_date: Mapped[datetime | None] = mapped_column(default=None)
    completed_at: Mapped[datetime | None] = mapped_column(default=None)
    verification_notes: Mapped[str | None] = mapped_column(Text, default=None)

    capa: Mapped[CAPA] = relationship(back_populates="actions")
    responsible: Mapped[object | None] = relationship("User")


class Evidence(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "evidence"

    finding_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("findings.id"))
    title: Mapped[str]
    file_path: Mapped[str | None] = mapped_column(default=None)
    evidence_type: Mapped[str] = mapped_column(default="document")
    description: Mapped[str | None] = mapped_column(Text, default=None)

    finding: Mapped[Finding] = relationship(back_populates="evidence_items")
