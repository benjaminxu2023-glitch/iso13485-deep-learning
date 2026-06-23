"""AI/ML medical-device (SaMD) audit models."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin


class SaMDRiskCategory(str, enum.Enum):
    """IMDRF Software as a Medical Device risk categories (I lowest .. IV highest)."""

    CATEGORY_I = "I"
    CATEGORY_II = "II"
    CATEGORY_III = "III"
    CATEGORY_IV = "IV"


class MLModelLifecycleStage(str, enum.Enum):
    PLANNING = "planning"
    DATA_COLLECTION = "data_collection"
    DEVELOPMENT = "development"
    VERIFICATION = "verification"
    VALIDATION = "validation"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    RETIREMENT = "retirement"


class MLModel(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ml_models"

    name: Mapped[str] = mapped_column(index=True)
    version: Mapped[str] = mapped_column(default="1.0.0")
    description: Mapped[str | None] = mapped_column(Text, default=None)
    model_type: Mapped[str] = mapped_column(default="classification")
    intended_use: Mapped[str | None] = mapped_column(Text, default=None)
    samd_risk_category: Mapped[SaMDRiskCategory | None] = mapped_column(default=None)
    lifecycle_stage: Mapped[MLModelLifecycleStage] = mapped_column(
        default=MLModelLifecycleStage.PLANNING
    )
    algorithm: Mapped[str | None] = mapped_column(default=None)
    framework: Mapped[str | None] = mapped_column(default=None)
    performance_metrics: Mapped[str | None] = mapped_column(Text, default=None)  # JSON
    predetermined_change_control_plan: Mapped[str | None] = mapped_column(Text, default=None)

    datasets: Mapped[list[MLDataset]] = relationship(
        back_populates="model", cascade="all, delete-orphan"
    )
    validations: Mapped[list[ModelValidation]] = relationship(
        back_populates="model", cascade="all, delete-orphan"
    )
    bias_assessments: Mapped[list[BiasAssessment]] = relationship(
        back_populates="model", cascade="all, delete-orphan"
    )


class MLDataset(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ml_datasets"

    model_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ml_models.id"))
    name: Mapped[str]
    purpose: Mapped[str] = mapped_column(default="training")  # training|validation|test
    size: Mapped[int | None] = mapped_column(default=None)
    source_description: Mapped[str | None] = mapped_column(Text, default=None)
    collection_methodology: Mapped[str | None] = mapped_column(Text, default=None)
    labeling_process: Mapped[str | None] = mapped_column(Text, default=None)
    demographics_summary: Mapped[str | None] = mapped_column(Text, default=None)  # JSON
    data_quality_score: Mapped[float | None] = mapped_column(default=None)
    integrity_hash: Mapped[str | None] = mapped_column(default=None)
    known_limitations: Mapped[str | None] = mapped_column(Text, default=None)

    model: Mapped[MLModel] = relationship(back_populates="datasets")


class ModelValidation(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "model_validations"

    model_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ml_models.id"))
    audit_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("audits.id"), default=None)
    validation_type: Mapped[str] = mapped_column(default="analytical")
    protocol_reference: Mapped[str | None] = mapped_column(default=None)
    results_summary: Mapped[str | None] = mapped_column(Text, default=None)
    pass_fail: Mapped[bool | None] = mapped_column(default=None)
    detailed_results: Mapped[str | None] = mapped_column(Text, default=None)  # JSON
    validated_by: Mapped[str | None] = mapped_column(default=None)
    validation_date: Mapped[datetime | None] = mapped_column(default=None)

    model: Mapped[MLModel] = relationship(back_populates="validations")


class BiasAssessment(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "bias_assessments"

    model_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ml_models.id"))
    audit_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("audits.id"), default=None)
    protected_attribute: Mapped[str]
    metric_name: Mapped[str]
    metric_value: Mapped[float]
    threshold: Mapped[float] = mapped_column(default=0.8)
    passes_threshold: Mapped[bool] = mapped_column(default=False)
    subgroup_details: Mapped[str | None] = mapped_column(Text, default=None)  # JSON
    mitigation_notes: Mapped[str | None] = mapped_column(Text, default=None)

    model: Mapped[MLModel] = relationship(back_populates="bias_assessments")
