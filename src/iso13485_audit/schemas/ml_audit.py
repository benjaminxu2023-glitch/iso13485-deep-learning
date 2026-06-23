"""Schemas for the AI/ML (SaMD) audit module."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from ..models.ml_audit import MLModelLifecycleStage, SaMDRiskCategory


class MLModelCreate(BaseModel):
    name: str
    version: str = "1.0.0"
    description: str | None = None
    model_type: str = "classification"
    intended_use: str | None = None
    algorithm: str | None = None
    framework: str | None = None
    lifecycle_stage: MLModelLifecycleStage = MLModelLifecycleStage.PLANNING


class MLModelUpdate(BaseModel):
    description: str | None = None
    intended_use: str | None = None
    algorithm: str | None = None
    framework: str | None = None
    lifecycle_stage: MLModelLifecycleStage | None = None
    samd_risk_category: SaMDRiskCategory | None = None
    performance_metrics: dict | None = None
    predetermined_change_control_plan: str | None = None


class MLModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: uuid.UUID
    name: str
    version: str
    description: str | None = None
    model_type: str
    intended_use: str | None = None
    samd_risk_category: SaMDRiskCategory | None = None
    lifecycle_stage: MLModelLifecycleStage
    algorithm: str | None = None
    framework: str | None = None


class DatasetCreate(BaseModel):
    name: str
    purpose: str = "training"
    size: int | None = None
    source_description: str | None = None
    collection_methodology: str | None = None
    labeling_process: str | None = None
    demographics_summary: dict | None = None
    known_limitations: str | None = None


class DatasetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: uuid.UUID
    model_id: uuid.UUID
    name: str
    purpose: str
    size: int | None = None
    data_quality_score: float | None = None


class ValidationCreate(BaseModel):
    validation_type: str = "analytical"
    protocol_reference: str | None = None
    results_summary: str | None = None
    pass_fail: bool | None = None
    detailed_results: dict | None = None
    validated_by: str | None = None
    validation_date: datetime | None = None


class ValidationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: uuid.UUID
    model_id: uuid.UUID
    validation_type: str
    pass_fail: bool | None = None
    results_summary: str | None = None


class BiasCheckRequest(BaseModel):
    """Predictions / labels / protected attributes for an automated bias audit."""

    predictions: list[float]
    labels: list[float] | None = None
    protected_attributes: dict[str, list[str]]
    thresholds: dict[str, float] | None = None


class BiasMetricResult(BaseModel):
    protected_attribute: str
    metric_name: str
    metric_value: float
    threshold: float
    passes_threshold: bool
    subgroup_details: dict | None = None


class BiasAuditResponse(BaseModel):
    model_id: uuid.UUID
    overall_passed: bool
    results: list[BiasMetricResult]


class SaMDClassifyRequest(BaseModel):
    significance: str  # treat_diagnose | drive | inform
    healthcare_situation: str  # critical | serious | non_serious


class SaMDClassifyResponse(BaseModel):
    significance: str
    healthcare_situation: str
    risk_category: SaMDRiskCategory
    level: str
    description: str
    requirements: list[str]


class LifecycleStatusResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_id: uuid.UUID
    current_stage: MLModelLifecycleStage
    completed_stages: list[str]
    next_stage: str | None = None
    required_artifacts: dict[str, list[str]]
    readiness_notes: list[str]
