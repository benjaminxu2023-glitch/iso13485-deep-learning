"""AI/ML (SaMD) audit endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...schemas.ml_audit import (
    BiasAuditResponse,
    BiasCheckRequest,
    DatasetCreate,
    DatasetResponse,
    LifecycleStatusResponse,
    MLModelCreate,
    MLModelResponse,
    MLModelUpdate,
    SaMDClassifyRequest,
    SaMDClassifyResponse,
    ValidationCreate,
    ValidationResponse,
)
from ...services import ml_audit_service
from ...services.ml_audit_service import MLAuditServiceError

router = APIRouter(prefix="/ml-audit", tags=["ml-audit"])


@router.post("/samd-classify", response_model=SaMDClassifyResponse)
def classify_samd(
    data: SaMDClassifyRequest, db: Session = Depends(get_db)
) -> SaMDClassifyResponse:
    try:
        return ml_audit_service.classify_samd(
            db, data.significance, data.healthcare_situation
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/models", response_model=MLModelResponse, status_code=201)
def register_model(data: MLModelCreate, db: Session = Depends(get_db)) -> MLModelResponse:
    model = ml_audit_service.register_model(db, data)
    db.commit()
    return model


@router.get("/models", response_model=list[MLModelResponse])
def list_models(db: Session = Depends(get_db)) -> list[MLModelResponse]:
    return ml_audit_service.list_models(db)


@router.get("/models/{model_id}", response_model=MLModelResponse)
def get_model(model_id: uuid.UUID, db: Session = Depends(get_db)) -> MLModelResponse:
    model = ml_audit_service.get_model(db, model_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.patch("/models/{model_id}", response_model=MLModelResponse)
def update_model(
    model_id: uuid.UUID, data: MLModelUpdate, db: Session = Depends(get_db)
) -> MLModelResponse:
    try:
        model = ml_audit_service.update_model(db, model_id, data)
    except MLAuditServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    db.commit()
    return model


@router.post(
    "/models/{model_id}/datasets", response_model=DatasetResponse, status_code=201
)
def add_dataset(
    model_id: uuid.UUID, data: DatasetCreate, db: Session = Depends(get_db)
) -> DatasetResponse:
    try:
        dataset = ml_audit_service.add_dataset(db, model_id, data)
    except MLAuditServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    db.commit()
    return dataset


@router.post(
    "/models/{model_id}/validations", response_model=ValidationResponse, status_code=201
)
def record_validation(
    model_id: uuid.UUID, data: ValidationCreate, db: Session = Depends(get_db)
) -> ValidationResponse:
    try:
        validation = ml_audit_service.record_validation(db, model_id, data)
    except MLAuditServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    db.commit()
    return validation


@router.post("/models/{model_id}/bias-check", response_model=BiasAuditResponse)
def bias_check(
    model_id: uuid.UUID, data: BiasCheckRequest, db: Session = Depends(get_db)
) -> BiasAuditResponse:
    try:
        result = ml_audit_service.run_bias_check(db, model_id, data)
    except MLAuditServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    db.commit()
    return result


@router.get("/models/{model_id}/lifecycle", response_model=LifecycleStatusResponse)
def lifecycle(
    model_id: uuid.UUID, db: Session = Depends(get_db)
) -> LifecycleStatusResponse:
    try:
        return ml_audit_service.get_lifecycle_status(db, model_id)
    except MLAuditServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
