"""AI/ML (SaMD) audit workflows: models, datasets, validations, bias and lifecycle."""

from __future__ import annotations

import json
import uuid

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..ml_validation.bias_detection import BiasDetector
from ..ml_validation.model_lifecycle import ModelLifecycleTracker
from ..ml_validation.samd_classifier import SaMDClassifier
from ..models import (
    BiasAssessment,
    MLDataset,
    MLModel,
    ModelValidation,
    SaMDRiskCategory,
)
from ..schemas.ml_audit import (
    BiasAuditResponse,
    BiasCheckRequest,
    BiasMetricResult,
    DatasetCreate,
    LifecycleStatusResponse,
    MLModelCreate,
    MLModelUpdate,
    SaMDClassifyResponse,
    ValidationCreate,
)


class MLAuditServiceError(Exception):
    """Raised for invalid ML-audit operations."""


# -- models ------------------------------------------------------------------
def register_model(session: Session, data: MLModelCreate) -> MLModel:
    model = MLModel(**data.model_dump())
    session.add(model)
    session.flush()
    return model


def get_model(session: Session, model_id: uuid.UUID) -> MLModel | None:
    stmt = (
        select(MLModel)
        .where(MLModel.id == model_id)
        .options(
            selectinload(MLModel.datasets),
            selectinload(MLModel.validations),
            selectinload(MLModel.bias_assessments),
        )
    )
    return session.scalar(stmt)


def list_models(session: Session) -> list[MLModel]:
    return list(session.scalars(select(MLModel).order_by(MLModel.created_at.desc())).all())


def update_model(session: Session, model_id: uuid.UUID, data: MLModelUpdate) -> MLModel:
    model = session.get(MLModel, model_id)
    if model is None:
        raise MLAuditServiceError(f"ML model {model_id} not found")
    payload = data.model_dump(exclude_unset=True)
    if "performance_metrics" in payload and payload["performance_metrics"] is not None:
        payload["performance_metrics"] = json.dumps(payload["performance_metrics"])
    for field, value in payload.items():
        setattr(model, field, value)
    session.flush()
    return model


# -- datasets ----------------------------------------------------------------
def add_dataset(session: Session, model_id: uuid.UUID, data: DatasetCreate) -> MLDataset:
    if session.get(MLModel, model_id) is None:
        raise MLAuditServiceError(f"ML model {model_id} not found")
    payload = data.model_dump()
    demographics = payload.pop("demographics_summary", None)
    dataset = MLDataset(
        model_id=model_id,
        demographics_summary=json.dumps(demographics) if demographics else None,
        **payload,
    )
    # Score the dataset's integrity from its metadata.
    from ..ml_validation.data_integrity import DataIntegrityAuditor

    report = DataIntegrityAuditor().audit_metadata(
        {**data.model_dump(), "demographics_summary": demographics}
    )
    dataset.data_quality_score = report.score
    session.add(dataset)
    session.flush()
    return dataset


# -- validations -------------------------------------------------------------
def record_validation(
    session: Session, model_id: uuid.UUID, data: ValidationCreate
) -> ModelValidation:
    if session.get(MLModel, model_id) is None:
        raise MLAuditServiceError(f"ML model {model_id} not found")
    payload = data.model_dump()
    detailed = payload.pop("detailed_results", None)
    validation = ModelValidation(
        model_id=model_id,
        detailed_results=json.dumps(detailed) if detailed else None,
        **payload,
    )
    session.add(validation)
    session.flush()
    return validation


# -- bias --------------------------------------------------------------------
def run_bias_check(
    session: Session, model_id: uuid.UUID, request: BiasCheckRequest
) -> BiasAuditResponse:
    if session.get(MLModel, model_id) is None:
        raise MLAuditServiceError(f"ML model {model_id} not found")

    predictions = np.asarray(request.predictions)
    labels = np.asarray(request.labels) if request.labels is not None else None
    protected = {k: np.asarray(v) for k, v in request.protected_attributes.items()}

    detector = BiasDetector()
    raw_results = detector.full_bias_audit(
        predictions=predictions,
        protected_attributes=protected,
        labels=labels,
        thresholds=request.thresholds,
    )

    results: list[BiasMetricResult] = []
    overall_passed = True
    for attr_name, metric in raw_results:
        overall_passed = overall_passed and metric.passes_threshold
        results.append(
            BiasMetricResult(
                protected_attribute=attr_name,
                metric_name=metric.metric_name,
                metric_value=metric.metric_value,
                threshold=metric.threshold,
                passes_threshold=metric.passes_threshold,
                subgroup_details=metric.subgroup_details,
            )
        )
        session.add(
            BiasAssessment(
                model_id=model_id,
                protected_attribute=attr_name,
                metric_name=metric.metric_name,
                metric_value=metric.metric_value,
                threshold=metric.threshold,
                passes_threshold=metric.passes_threshold,
                subgroup_details=json.dumps(metric.subgroup_details),
            )
        )
    session.flush()
    return BiasAuditResponse(
        model_id=model_id, overall_passed=overall_passed, results=results
    )


# -- SaMD classification -----------------------------------------------------
def classify_samd(
    session: Session,
    significance: str,
    healthcare_situation: str,
    model_id: uuid.UUID | None = None,
) -> SaMDClassifyResponse:
    classifier = SaMDClassifier()
    category: SaMDRiskCategory = classifier.classify(significance, healthcare_situation)
    info = classifier.describe(category)

    if model_id is not None:
        model = session.get(MLModel, model_id)
        if model is not None:
            model.samd_risk_category = category
            session.flush()

    return SaMDClassifyResponse(
        significance=significance,
        healthcare_situation=healthcare_situation,
        risk_category=category,
        level=info["level"],
        description=info["description"],
        requirements=info["requirements"],
    )


# -- lifecycle ---------------------------------------------------------------
def get_lifecycle_status(
    session: Session, model_id: uuid.UUID
) -> LifecycleStatusResponse:
    model = get_model(session, model_id)
    if model is None:
        raise MLAuditServiceError(f"ML model {model_id} not found")

    tracker = ModelLifecycleTracker()
    fields = {
        "intended_use": model.intended_use,
        "samd_risk_category": model.samd_risk_category,
        "predetermined_change_control_plan": model.predetermined_change_control_plan,
        "has_validation": len(model.validations) > 0,
        "has_bias_assessment": len(model.bias_assessments) > 0,
    }
    return LifecycleStatusResponse(
        model_id=model_id,
        current_stage=model.lifecycle_stage,
        completed_stages=tracker.completed_stages(model.lifecycle_stage),
        next_stage=tracker.next_stage(model.lifecycle_stage),
        required_artifacts=tracker.required_artifacts(model.lifecycle_stage),
        readiness_notes=tracker.readiness_notes(fields, model.lifecycle_stage),
    )
