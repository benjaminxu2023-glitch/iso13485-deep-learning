"""Document upload and gap-analysis endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import DocumentType
from ...schemas.documents import AnalysisResponse, DocumentResponse
from ...services import document_service
from ...services.document_service import DocumentServiceError

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    document_type: DocumentType = Form(DocumentType.OTHER),
    version: str | None = Form(None),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    raw = await file.read()
    stored = document_service.store_uploaded_file(file.filename or "upload", raw)
    try:
        document = document_service.create_document(
            db,
            title=title,
            file_path=stored,
            document_type=document_type,
            version=version,
        )
    except DocumentServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    return document


@router.get("", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)) -> list[DocumentResponse]:
    return document_service.list_documents(db)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: uuid.UUID, db: Session = Depends(get_db)) -> DocumentResponse:
    document = document_service.get_document(db, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.post("/{document_id}/analyze", response_model=AnalysisResponse)
def analyze_document(
    document_id: uuid.UUID, db: Session = Depends(get_db)
) -> AnalysisResponse:
    try:
        analysis = document_service.analyze_document(db, document_id)
    except DocumentServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    db.commit()
    return analysis


@router.get("/{document_id}/gaps", response_model=AnalysisResponse)
def get_gaps(document_id: uuid.UUID, db: Session = Depends(get_db)) -> AnalysisResponse:
    analysis = document_service.get_latest_analysis(db, document_id)
    if analysis is None:
        raise HTTPException(
            status_code=404, detail="No analysis found; run analyze first"
        )
    return analysis
