"""Threshold-based compliance-gap detection from a coverage matrix."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..models import ISORequirement


@dataclass
class GapResult:
    """A detected compliance gap for a single ISO requirement."""

    requirement: ISORequirement
    best_similarity: float
    severity: str
    confidence: float
    recommendation: str


class GapDetector:
    """Flags ISO requirements that are not adequately covered by a document.

    A requirement is considered a gap when the best similarity of any document
    section to that requirement falls below ``similarity_threshold``.
    """

    def __init__(
        self,
        similarity_threshold: float = 0.12,
        high_confidence_threshold: float = 0.30,
    ):
        self.similarity_threshold = similarity_threshold
        self.high_confidence_threshold = high_confidence_threshold

    def detect(
        self,
        coverage_matrix: np.ndarray,  # shape: (n_requirements, n_sections)
        requirements: list[ISORequirement],
    ) -> list[GapResult]:
        gaps: list[GapResult] = []
        for idx, requirement in enumerate(requirements):
            if coverage_matrix.shape[1] == 0:
                best = 0.0
            else:
                best = float(np.max(coverage_matrix[idx]))
            if best < self.similarity_threshold:
                gaps.append(
                    GapResult(
                        requirement=requirement,
                        best_similarity=best,
                        severity=self._severity(requirement.risk_weight, best),
                        confidence=self._confidence(best),
                        recommendation=self._recommend(requirement),
                    )
                )
        return gaps

    def coverage_score(self, coverage_matrix: np.ndarray) -> float:
        """Fraction of requirements with at least threshold-level coverage (0..1)."""
        if coverage_matrix.shape[0] == 0:
            return 0.0
        best_per_req = (
            np.max(coverage_matrix, axis=1)
            if coverage_matrix.shape[1] > 0
            else np.zeros(coverage_matrix.shape[0])
        )
        covered = np.sum(best_per_req >= self.similarity_threshold)
        return float(covered / coverage_matrix.shape[0])

    def _severity(self, risk_weight: int, best: float) -> str:
        # Higher requirement risk and lower coverage => higher gap severity.
        if risk_weight >= 5:
            return "high"
        if risk_weight >= 3:
            return "medium" if best > 0 else "high"
        return "low"

    def _confidence(self, best: float) -> float:
        # Confidence that this is a genuine gap: 1.0 when zero coverage,
        # decreasing as similarity approaches the threshold.
        if self.similarity_threshold <= 0:
            return 1.0
        return round(float(max(0.0, 1.0 - best / self.similarity_threshold)), 4)

    def _recommend(self, requirement: ISORequirement) -> str:
        clause_number = requirement.clause.clause_number if requirement.clause else "?"
        guidance = requirement.evidence_guidance or "documented evidence of conformity"
        return (
            f"Document does not appear to address ISO 13485 clause {clause_number}. "
            f"Add or reference {guidance.lower()}."
        )
