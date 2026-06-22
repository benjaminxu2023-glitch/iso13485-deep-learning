"""Dataset integrity auditing: completeness, lineage, drift and hash verification."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class IntegrityReport:
    score: float  # 0..1 overall data-quality score
    completeness_issues: list[str]
    lineage_issues: list[str]
    passed: bool


class DataIntegrityAuditor:
    """Audits ML dataset metadata for regulatory completeness and lineage."""

    LINEAGE_FIELDS = ("source_description", "collection_methodology", "labeling_process")

    def audit_metadata(self, dataset_metadata: dict) -> IntegrityReport:
        completeness_issues: list[str] = []
        lineage_issues: list[str] = []

        size = dataset_metadata.get("size")
        if not size:
            completeness_issues.append("Dataset size is not recorded.")
        elif size < 100:
            completeness_issues.append(
                f"Dataset size ({size}) may be inadequate for validation."
            )

        if not dataset_metadata.get("demographics_summary"):
            completeness_issues.append(
                "No demographic representation recorded; cannot assess population coverage."
            )

        for field in self.LINEAGE_FIELDS:
            if not dataset_metadata.get(field):
                lineage_issues.append(f"Missing lineage information: {field}.")

        total_checks = 2 + len(self.LINEAGE_FIELDS)
        failed = len(completeness_issues) + len(lineage_issues)
        score = max(0.0, 1.0 - failed / total_checks)
        return IntegrityReport(
            score=round(score, 4),
            completeness_issues=completeness_issues,
            lineage_issues=lineage_issues,
            passed=failed == 0,
        )

    def population_stability_index(
        self, reference: np.ndarray, current: np.ndarray, bins: int = 10
    ) -> float:
        """Population Stability Index between two continuous distributions.

        PSI < 0.1 = no significant shift, 0.1-0.25 = moderate, > 0.25 = major drift.
        """
        reference = np.asarray(reference, dtype=float)
        current = np.asarray(current, dtype=float)
        if reference.size == 0 or current.size == 0:
            return 0.0
        quantiles = np.linspace(0, 1, bins + 1)
        edges = np.unique(np.quantile(reference, quantiles))
        if edges.size < 2:
            return 0.0
        ref_counts, _ = np.histogram(reference, bins=edges)
        cur_counts, _ = np.histogram(current, bins=edges)
        ref_pct = ref_counts / max(1, ref_counts.sum())
        cur_pct = cur_counts / max(1, cur_counts.sum())
        eps = 1e-6
        ref_pct = np.clip(ref_pct, eps, None)
        cur_pct = np.clip(cur_pct, eps, None)
        psi = np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct))
        return round(float(psi), 4)

    def verify_file_integrity(self, file_path: str | Path, expected_hash: str) -> bool:
        data = Path(file_path).read_bytes()
        return hashlib.sha256(data).hexdigest() == expected_hash
