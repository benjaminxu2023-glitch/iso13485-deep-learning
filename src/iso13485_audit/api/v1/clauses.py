"""Clause endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...database import get_db
from ...schemas.clauses import ClauseDetail, ClauseResponse
from ...services import clause_service

router = APIRouter(prefix="/clauses", tags=["clauses"])


@router.get("", response_model=list[ClauseResponse])
def list_clauses(
    top_level_only: bool = Query(False),
    db: Session = Depends(get_db),
) -> list[ClauseResponse]:
    return clause_service.list_clauses(db, top_level_only=top_level_only)


@router.get("/search", response_model=list[ClauseResponse])
def search_clauses(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    return clause_service.search_clauses(db, q)


@router.get("/{clause_id}", response_model=ClauseDetail)
def get_clause(clause_id: uuid.UUID, db: Session = Depends(get_db)) -> ClauseDetail:
    clause = clause_service.get_clause(db, clause_id)
    if clause is None:
        raise HTTPException(status_code=404, detail="Clause not found")
    return clause
