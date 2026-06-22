"""Schemas for findings, CAPAs, CAPA actions and evidence."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from ..models.findings import (
    CAPAStatus,
    CAPAType,
    FindingSeverity,
    FindingStatus,
)


class FindingCreate(BaseModel):
    audit_id: uuid.UUID
    title: str
    description: str
    severity: FindingSeverity = FindingSeverity.MINOR_NC
    checklist_item_id: uuid.UUID | None = None
    clause_id: uuid.UUID | None = None
    objective_evidence: str | None = None
    due_date: datetime | None = None


class FindingUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    severity: FindingSeverity | None = None
    status: FindingStatus | None = None
    objective_evidence: str | None = None
    due_date: datetime | None = None


class FindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    audit_id: uuid.UUID
    checklist_item_id: uuid.UUID | None = None
    clause_id: uuid.UUID | None = None
    title: str
    description: str
    objective_evidence: str | None = None
    severity: FindingSeverity
    status: FindingStatus
    due_date: datetime | None = None
    created_at: datetime


class CAPAActionCreate(BaseModel):
    description: str
    action_type: str = "corrective"
    responsible_id: uuid.UUID | None = None
    due_date: datetime | None = None


class CAPAActionUpdate(BaseModel):
    description: str | None = None
    completed_at: datetime | None = None
    verification_notes: str | None = None


class CAPAActionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    capa_id: uuid.UUID
    description: str
    action_type: str
    responsible_id: uuid.UUID | None = None
    due_date: datetime | None = None
    completed_at: datetime | None = None
    verification_notes: str | None = None


class CAPACreate(BaseModel):
    finding_id: uuid.UUID
    capa_type: CAPAType = CAPAType.CORRECTIVE
    root_cause: str | None = None
    risk_assessment: str | None = None
    owner_id: uuid.UUID | None = None
    target_completion: datetime | None = None
    effectiveness_criteria: str | None = None


class CAPAUpdate(BaseModel):
    status: CAPAStatus | None = None
    capa_type: CAPAType | None = None
    root_cause: str | None = None
    risk_assessment: str | None = None
    owner_id: uuid.UUID | None = None
    target_completion: datetime | None = None
    actual_completion: datetime | None = None
    effectiveness_criteria: str | None = None
    effectiveness_result: str | None = None


class CAPAResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    finding_id: uuid.UUID
    capa_number: str
    capa_type: CAPAType
    status: CAPAStatus
    root_cause: str | None = None
    risk_assessment: str | None = None
    owner_id: uuid.UUID | None = None
    target_completion: datetime | None = None
    actual_completion: datetime | None = None
    effectiveness_criteria: str | None = None
    effectiveness_result: str | None = None
    actions: list[CAPAActionResponse] = []


class EffectivenessCheck(BaseModel):
    effectiveness_result: str
    passed: bool


class FindingStatistics(BaseModel):
    total: int
    by_severity: dict[str, int]
    by_status: dict[str, int]
    open_count: int
    closed_count: int
