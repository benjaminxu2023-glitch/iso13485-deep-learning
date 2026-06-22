"""Schemas for ISO clauses and requirements."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict


class RequirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    requirement_text: str
    requirement_type: str
    evidence_guidance: str | None = None
    risk_weight: int


class ClauseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    clause_number: str
    title: str
    description: str | None = None
    clause_level: int
    is_mandatory: bool
    fda_820_reference: str | None = None
    parent_id: uuid.UUID | None = None


class ClauseDetail(ClauseResponse):
    requirements: list[RequirementResponse] = []
    children: list[ClauseResponse] = []
