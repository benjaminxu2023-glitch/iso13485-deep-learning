"""Tests for the clause service and seed data."""

from __future__ import annotations

from iso13485_audit.services import clause_service


def test_seed_creates_full_hierarchy(seeded_session):
    top = clause_service.list_clauses(seeded_session, top_level_only=True)
    assert [c.clause_number for c in top] == ["4", "5", "6", "7", "8"]


def test_get_clause_by_number_with_children(seeded_session):
    clause = clause_service.get_clause_by_number(seeded_session, "7.3")
    assert clause is not None
    assert clause.title == "Design and Development"
    child_numbers = {c.clause_number for c in clause.children}
    assert "7.3.2" in child_numbers
    assert "7.3.7" in child_numbers


def test_fda_820_cross_reference(seeded_session):
    clause = clause_service.get_clause_by_number(seeded_session, "7.3.7")
    assert clause.fda_820_reference is not None
    assert "820.30" in clause.fda_820_reference


def test_expand_clause_numbers_includes_descendants(seeded_session):
    clauses = clause_service.expand_clause_numbers(seeded_session, ["7.3"])
    numbers = {c.clause_number for c in clauses}
    assert "7.3" in numbers
    assert "7.3.10" in numbers
    # Should not pull in unrelated clauses.
    assert "7.4" not in numbers


def test_requirements_for_clause_numbers(seeded_session):
    reqs = clause_service.requirements_for_clause_numbers(seeded_session, ["8.5.2"])
    assert len(reqs) >= 1
    assert all(r.clause.clause_number.startswith("8.5.2") for r in reqs)


def test_search_clauses(seeded_session):
    results = clause_service.search_clauses(seeded_session, "design")
    assert any("Design" in c.title for c in results)


def test_seed_is_idempotent(seeded_session):
    before = len(clause_service.list_clauses(seeded_session))
    from iso13485_audit.seed_data import seed_all

    seed_all(seeded_session)
    after = len(clause_service.list_clauses(seeded_session))
    assert before == after
