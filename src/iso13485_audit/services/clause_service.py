"""Clause CRUD, hierarchy traversal and search."""

from __future__ import annotations

import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from ..models import ISOClause, ISORequirement


def list_clauses(session: Session, top_level_only: bool = False) -> list[ISOClause]:
    stmt = select(ISOClause).order_by(ISOClause.clause_number)
    if top_level_only:
        stmt = stmt.where(ISOClause.parent_id.is_(None))
    return list(session.scalars(stmt).all())


def get_clause(session: Session, clause_id: uuid.UUID) -> ISOClause | None:
    stmt = (
        select(ISOClause)
        .where(ISOClause.id == clause_id)
        .options(selectinload(ISOClause.requirements), selectinload(ISOClause.children))
    )
    return session.scalar(stmt)


def get_clause_by_number(session: Session, clause_number: str) -> ISOClause | None:
    stmt = (
        select(ISOClause)
        .where(ISOClause.clause_number == clause_number)
        .options(selectinload(ISOClause.requirements), selectinload(ISOClause.children))
    )
    return session.scalar(stmt)


def get_requirements(session: Session, clause_id: uuid.UUID) -> list[ISORequirement]:
    stmt = select(ISORequirement).where(ISORequirement.clause_id == clause_id)
    return list(session.scalars(stmt).all())


def search_clauses(session: Session, query: str) -> list[ISOClause]:
    pattern = f"%{query.lower()}%"
    stmt = select(ISOClause).where(
        or_(
            ISOClause.title.ilike(pattern),
            ISOClause.description.ilike(pattern),
            ISOClause.clause_number.ilike(pattern),
        )
    ).order_by(ISOClause.clause_number)
    return list(session.scalars(stmt).all())


def expand_clause_numbers(session: Session, clause_numbers: list[str]) -> list[ISOClause]:
    """Resolve clause numbers to clauses, including all descendants of each.

    Passing "7.3" returns 7.3 and every sub-clause (7.3.1, 7.3.2, ...).
    """
    selected: dict[str, ISOClause] = {}
    all_clauses = list_clauses(session)
    for number in clause_numbers:
        prefix = number + "."
        for clause in all_clauses:
            if clause.clause_number == number or clause.clause_number.startswith(prefix):
                selected[clause.clause_number] = clause
    return sorted(selected.values(), key=lambda c: _sort_key(c.clause_number))


def requirements_for_clause_numbers(
    session: Session, clause_numbers: list[str]
) -> list[ISORequirement]:
    """Return all requirements belonging to the given clauses and their descendants."""
    clauses = expand_clause_numbers(session, clause_numbers)
    clause_ids = [c.id for c in clauses]
    if not clause_ids:
        return []
    stmt = (
        select(ISORequirement)
        .where(ISORequirement.clause_id.in_(clause_ids))
        .options(selectinload(ISORequirement.clause))
    )
    return list(session.scalars(stmt).all())


def all_requirements(session: Session) -> list[ISORequirement]:
    stmt = select(ISORequirement).options(selectinload(ISORequirement.clause))
    return list(session.scalars(stmt).all())


def _sort_key(clause_number: str) -> tuple[int, ...]:
    return tuple(int(p) for p in clause_number.split(".") if p.isdigit())
