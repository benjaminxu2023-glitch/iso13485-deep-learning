"""Document upload, text extraction and analysis orchestration."""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..config import get_settings
from ..models import Document, DocumentAnalysis, DocumentType
from ..nlp.document_analyzer import DocumentAnalyzer
from ..nlp.preprocessing import extract_text


class DocumentServiceError(Exception):
    """Raised for invalid document operations."""


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def store_uploaded_file(filename: str, data: bytes) -> Path:
    """Persist raw upload bytes under the configured upload directory."""
    settings = get_settings()
    settings.ensure_dirs()
    safe_name = f"{uuid.uuid4().hex}_{Path(filename).name}"
    dest = settings.upload_dir / safe_name
    dest.write_bytes(data)
    return dest


def create_document(
    session: Session,
    *,
    title: str,
    file_path: str | Path,
    document_type: DocumentType = DocumentType.OTHER,
    document_number: str | None = None,
    version: str | None = None,
) -> Document:
    path = Path(file_path)
    if not path.exists():
        raise DocumentServiceError(f"File not found: {path}")

    raw = path.read_bytes()
    text = extract_text(path)
    document = Document(
        title=title,
        document_number=document_number,
        document_type=document_type,
        version=version,
        file_path=str(path),
        file_hash=_hash_bytes(raw),
        content_text=text,
    )
    session.add(document)
    session.flush()
    return document


def get_document(session: Session, document_id: uuid.UUID) -> Document | None:
    return session.get(Document, document_id)


def list_documents(session: Session) -> list[Document]:
    stmt = select(Document).order_by(Document.upload_date.desc())
    return list(session.scalars(stmt).all())


def analyze_document(session: Session, document_id: uuid.UUID) -> DocumentAnalysis:
    if get_document(session, document_id) is None:
        raise DocumentServiceError(f"Document {document_id} not found")
    analyzer = DocumentAnalyzer(session)
    return analyzer.analyze(document_id)


def get_latest_analysis(
    session: Session, document_id: uuid.UUID
) -> DocumentAnalysis | None:
    stmt = (
        select(DocumentAnalysis)
        .where(DocumentAnalysis.document_id == document_id)
        .order_by(DocumentAnalysis.created_at.desc())
        .options(selectinload(DocumentAnalysis.gaps))
        .limit(1)
    )
    return session.scalar(stmt)
