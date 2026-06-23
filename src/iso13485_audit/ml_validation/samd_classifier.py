"""IMDRF Software as a Medical Device (SaMD) risk categorization."""

from __future__ import annotations

from ..models.ml_audit import SaMDRiskCategory
from ..seed_data import load_samd_categories

VALID_SIGNIFICANCE = {"treat_diagnose", "drive", "inform"}
VALID_SITUATION = {"critical", "serious", "non_serious"}


class SaMDClassifier:
    """Classifies SaMD risk per the IMDRF framework matrix."""

    def __init__(self) -> None:
        self._data = load_samd_categories()
        self._matrix = self._data["risk_matrix"]
        self._categories = self._data["categories"]

    def classify(self, significance: str, healthcare_situation: str) -> SaMDRiskCategory:
        significance = significance.strip().lower()
        healthcare_situation = healthcare_situation.strip().lower()
        if significance not in VALID_SIGNIFICANCE:
            raise ValueError(
                f"significance must be one of {sorted(VALID_SIGNIFICANCE)}"
            )
        if healthcare_situation not in VALID_SITUATION:
            raise ValueError(
                f"healthcare_situation must be one of {sorted(VALID_SITUATION)}"
            )
        key = f"{significance}|{healthcare_situation}"
        return SaMDRiskCategory(self._matrix[key])

    def describe(self, category: SaMDRiskCategory) -> dict:
        info = self._categories[category.value]
        return {
            "level": info["level"],
            "description": info["description"],
            "requirements": info["requirements"],
        }

    def get_regulatory_requirements(self, category: SaMDRiskCategory) -> list[str]:
        return self._categories[category.value]["requirements"]
