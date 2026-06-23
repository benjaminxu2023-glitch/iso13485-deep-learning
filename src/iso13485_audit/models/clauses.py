"""ISO 13485 clause hierarchy and requirement models."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin


class ISOClause(UUIDMixin, TimestampMixin, Base):
    """A single clause of ISO 13485:2016, arranged as a self-referential tree."""

    __tablename__ = "iso_clauses"

    clause_number: Mapped[str] = mapped_column(index=True)  # e.g. "4.1", "7.3.2"
    title: Mapped[str]
    description: Mapped[str | None] = mapped_column(Text, default=None)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("iso_clauses.id"), default=None
    )
    clause_level: Mapped[int] = mapped_column(default=1)  # 1=section, 2=sub, 3=sub-sub
    is_mandatory: Mapped[bool] = mapped_column(default=True)
    fda_820_reference: Mapped[str | None] = mapped_column(default=None)

    parent: Mapped[ISOClause | None] = relationship(
        back_populates="children", remote_side="ISOClause.id"
    )
    children: Mapped[list[ISOClause]] = relationship(
        back_populates="parent", cascade="all, delete-orphan"
    )
    requirements: Mapped[list[ISORequirement]] = relationship(
        back_populates="clause", cascade="all, delete-orphan"
    )


class ISORequirement(UUIDMixin, TimestampMixin, Base):
    """An individual normative ("shall") requirement attached to a clause."""

    __tablename__ = "iso_requirements"

    clause_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("iso_clauses.id"))
    requirement_text: Mapped[str] = mapped_column(Text)
    requirement_type: Mapped[str] = mapped_column(default="shall")  # shall | should | may
    evidence_guidance: Mapped[str | None] = mapped_column(Text, default=None)
    risk_weight: Mapped[int] = mapped_column(default=3)  # 1 (low) .. 5 (high)

    clause: Mapped[ISOClause] = relationship(back_populates="requirements")
