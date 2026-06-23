"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .. import __version__
from ..config import get_settings
from .v1 import build_v1_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="ISO 13485 Audit System",
        version=__version__,
        description=(
            "ISO 13485:2016 audit management with an AI/ML (SaMD) audit module: "
            "clause engine, audit checklists, findings/CAPA, NLP gap detection, "
            "bias/SaMD analysis and reporting."
        ),
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(ValueError)
    async def _value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.get("/health", tags=["meta"])
    def health() -> dict:
        return {"status": "ok", "version": __version__, "nlp_backend": settings.nlp_backend}

    app.include_router(build_v1_router(), prefix=settings.api_prefix)
    return app
