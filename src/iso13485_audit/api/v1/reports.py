"""Report generation and download endpoints."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ...database import get_db
from ...reports.generator import ReportError
from ...schemas.reports import ReportGenerateRequest, ReportResponse
from ...services import report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/generate", response_model=ReportResponse)
def generate_report(
    data: ReportGenerateRequest, db: Session = Depends(get_db)
) -> ReportResponse:
    try:
        return report_service.generate_report(
            db, data.report_type, data.target_id, data.format
        )
    except ReportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ImportError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc


@router.get("/download")
def download_report(path: str) -> FileResponse:
    file_path = Path(path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")
    return FileResponse(str(file_path), filename=file_path.name)
