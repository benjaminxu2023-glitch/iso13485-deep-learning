"""Version 1 API router aggregation."""

from __future__ import annotations

from fastapi import APIRouter

from . import audits, capa, clauses, documents, findings, ml_audit, reports, users


def build_v1_router() -> APIRouter:
    router = APIRouter()
    router.include_router(clauses.router)
    router.include_router(audits.router)
    router.include_router(findings.router)
    router.include_router(capa.router)
    router.include_router(documents.router)
    router.include_router(ml_audit.router)
    router.include_router(reports.router)
    router.include_router(users.router)
    return router
