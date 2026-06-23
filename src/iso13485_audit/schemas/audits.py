"""Schemas for audits, checklists and checklist items."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from ..models.audits import AuditStatus, AuditType, ConformityStatus


class AuditCreate(BaseModel):
    title: str
    audit_type: AuditType = AuditType.INTERNAL
    scope_description: str | None = None
    lead_auditor_id: uuid.UUID | None = None
    planned_start: datetime | None = None
    planned_end: datetime | None = None


class AuditUpdate(BaseModel):
    title: str | None = None
    status: AuditStatus | None = None
    scope_description: str | None = None
    lead_auditor_id: uuid.UUID | None = None
    planned_start: datetime | None = None
    planned_end: datetime | None = None
    actual_start: datetime | None = None
    actual_end: datetime | None = None


class AuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    audit_type: AuditType
    status: AuditStatus
    scope_description: str | None = None
    lead_auditor_id: uuid.UUID | None = None
    planned_start: datetime | None = None
    planned_end: datetime | None = None
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    created_at: datetime


class ChecklistItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    checklist_id: uuid.UUID
    requirement_id: uuid.UUID | None = None
    clause_number: str | None = None
    question: str
    guidance_notes: str | None = None
    conformity_status: ConformityStatus
    auditor_notes: str | None = None
    evidence_reference: str | None = None
    sort_order: int


class ChecklistItemUpdate(BaseModel):
    conformity_status: ConformityStatus | None = None
    auditor_notes: str | None = None
    evidence_reference: str | None = None


class ChecklistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    audit_id: uuid.UUID
    template_id: uuid.UUID | None = None
    title: str
    completed_at: datetime | None = None
    items: list[ChecklistItemResponse] = []


class ChecklistCreate(BaseModel):
    title: str | None = None
    template_id: uuid.UUID | None = None
    template_name: str | None = None
    clause_numbers: list[str] | None = None


class AuditSummary(BaseModel):
    audit_id: uuid.UUID
    total_items: int
    assessed_items: int
    conforming: int
    nonconforming: int
    observations: int
    not_applicable: int
    not_assessed: int
    conformity_rate: float
    findings_count: int
