"""Seed reference data: ISO 13485 clauses, FDA 820 mapping and checklist templates."""

from __future__ import annotations

import json
from importlib import resources

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import ChecklistTemplate, ISOClause, ISORequirement

_PACKAGE = "iso13485_audit.seed_data"


def _load_json(filename: str):
    with resources.files(_PACKAGE).joinpath(filename).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_clause_data() -> list[dict]:
    return _load_json("iso13485_clauses.json")


def load_fda_mapping() -> dict[str, str]:
    return _load_json("fda_820_mapping.json")


def load_templates() -> list[dict]:
    return _load_json("checklist_templates.json")


def load_samd_categories() -> dict:
    return _load_json("samd_categories.json")


def seed_clauses(session: Session) -> int:
    """Insert the ISO 13485 clause hierarchy and requirements.

    Idempotent: existing clauses (matched by ``clause_number``) are skipped.
    Returns the number of newly created clauses.
    """
    clauses = load_clause_data()
    fda_map = load_fda_mapping()

    existing = {c.clause_number for c in session.scalars(select(ISOClause)).all()}
    number_to_clause: dict[str, ISOClause] = {}
    created = 0

    # First pass: create clauses (parents appear before children in the file).
    for entry in clauses:
        number = entry["clause_number"]
        if number in existing:
            number_to_clause[number] = session.scalar(
                select(ISOClause).where(ISOClause.clause_number == number)
            )
            continue

        parent_number = _parent_number(number)
        parent = number_to_clause.get(parent_number)
        clause = ISOClause(
            clause_number=number,
            title=entry["title"],
            description=entry.get("description"),
            clause_level=entry.get("level", number.count(".") + 1),
            fda_820_reference=fda_map.get(number),
            parent_id=parent.id if parent else None,
        )
        session.add(clause)
        session.flush()  # assign id for child references
        number_to_clause[number] = clause
        created += 1

        for req in entry.get("requirements", []):
            session.add(
                ISORequirement(
                    clause_id=clause.id,
                    requirement_text=req["text"],
                    requirement_type=req.get("type", "shall"),
                    evidence_guidance=req.get("evidence_guidance"),
                    risk_weight=req.get("risk_weight", 3),
                )
            )

    return created


def seed_templates(session: Session) -> int:
    """Insert the default checklist templates. Idempotent by template name."""
    templates = load_templates()
    existing = {t.name for t in session.scalars(select(ChecklistTemplate)).all()}
    created = 0
    for entry in templates:
        if entry["name"] in existing:
            continue
        session.add(
            ChecklistTemplate(
                name=entry["name"],
                description=entry.get("description"),
                audit_type=entry.get("audit_type", "internal"),
                is_default=entry.get("is_default", False),
                template_data=json.dumps({"clauses": entry.get("clauses", [])}),
            )
        )
        created += 1
    return created


def seed_all(session: Session) -> dict[str, int]:
    """Seed clauses and templates. Returns counts of created records."""
    clauses = seed_clauses(session)
    session.flush()
    templates = seed_templates(session)
    return {"clauses": clauses, "templates": templates}


def _parent_number(clause_number: str) -> str:
    """Return the parent clause number, e.g. "7.3.2" -> "7.3", "7" -> ""."""
    parts = clause_number.split(".")
    if len(parts) <= 1:
        return ""
    return ".".join(parts[:-1])
