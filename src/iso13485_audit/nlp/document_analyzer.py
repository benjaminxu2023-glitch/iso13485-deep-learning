"""Orchestrates document gap analysis: text -> sections -> coverage -> gaps."""

from __future__ import annotations

import json
import uuid

import numpy as np
from sqlalchemy.orm import Session

from ..models import ComplianceGap, Document, DocumentAnalysis
from ..services import clause_service
from .engine import NLPEngine, get_default_engine
from .gap_detector import GapDetector
from .preprocessing import split_sections


class DocumentAnalyzer:
    """Runs the full compliance-gap analysis pipeline for a document."""

    def __init__(
        self,
        session: Session,
        engine: NLPEngine | None = None,
        detector: GapDetector | None = None,
    ):
        self.session = session
        self.engine = engine or get_default_engine()
        if detector is None:
            from ..config import get_settings

            settings = get_settings()
            detector = GapDetector(
                similarity_threshold=settings.gap_similarity_threshold,
                high_confidence_threshold=settings.gap_high_confidence_threshold,
            )
        self.detector = detector

    def analyze(self, document_id: uuid.UUID) -> DocumentAnalysis:
        document = self.session.get(Document, document_id)
        if document is None:
            raise ValueError(f"Document {document_id} not found")

        text = document.content_text or ""
        sections = split_sections(text)
        section_texts = [s.text for s in sections]

        requirements = clause_service.all_requirements(self.session)
        requirement_texts = [
            f"{r.clause.clause_number} {r.clause.title}. {r.requirement_text}"
            for r in requirements
        ]

        # Fit TF-IDF on the combined corpus so both sides share a vocabulary.
        self.engine.fit(requirement_texts + section_texts)
        req_emb = self.engine.encode(requirement_texts)
        sec_emb = self.engine.encode(section_texts)
        coverage = self.engine.similarity_matrix(req_emb, sec_emb)  # (n_req, n_sec)

        gaps = self.detector.detect(coverage, requirements)
        score = self.detector.coverage_score(coverage)

        analysis = DocumentAnalysis(
            document_id=document.id,
            analysis_type="gap_detection",
            overall_score=round(score, 4),
            summary=(
                f"Assessed {len(requirements)} requirements across {len(sections)} "
                f"document sections. Coverage {score:.0%}; {len(gaps)} gap(s) detected."
            ),
            raw_results=json.dumps(
                {
                    "n_requirements": len(requirements),
                    "n_sections": len(sections),
                    "coverage_score": round(score, 4),
                    "n_gaps": len(gaps),
                    "backend": self.engine.backend,
                }
            ),
        )
        self.session.add(analysis)
        self.session.flush()

        for gap in gaps:
            clause = gap.requirement.clause
            best_section_idx = (
                int(np.argmax(coverage[requirements.index(gap.requirement)]))
                if coverage.shape[1] > 0
                else None
            )
            excerpt = (
                section_texts[best_section_idx][:300]
                if best_section_idx is not None and section_texts
                else None
            )
            self.session.add(
                ComplianceGap(
                    analysis_id=analysis.id,
                    clause_id=clause.id if clause else None,
                    clause_number=clause.clause_number if clause else None,
                    gap_description=(
                        f"Insufficient coverage of requirement under clause "
                        f"{clause.clause_number if clause else '?'}: "
                        f"{gap.requirement.requirement_text[:200]}"
                    ),
                    severity=gap.severity,
                    confidence=gap.confidence,
                    document_excerpt=excerpt,
                    recommendation=gap.recommendation,
                )
            )

        self.session.flush()
        self.session.refresh(analysis)
        return analysis
