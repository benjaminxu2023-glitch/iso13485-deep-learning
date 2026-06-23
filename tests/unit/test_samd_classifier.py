"""Tests for the IMDRF SaMD classifier."""

from __future__ import annotations

import pytest

from iso13485_audit.ml_validation.samd_classifier import SaMDClassifier
from iso13485_audit.models.ml_audit import SaMDRiskCategory


@pytest.mark.parametrize(
    ("significance", "situation", "expected"),
    [
        ("treat_diagnose", "critical", SaMDRiskCategory.CATEGORY_IV),
        ("treat_diagnose", "serious", SaMDRiskCategory.CATEGORY_III),
        ("treat_diagnose", "non_serious", SaMDRiskCategory.CATEGORY_II),
        ("drive", "critical", SaMDRiskCategory.CATEGORY_III),
        ("drive", "serious", SaMDRiskCategory.CATEGORY_II),
        ("drive", "non_serious", SaMDRiskCategory.CATEGORY_I),
        ("inform", "critical", SaMDRiskCategory.CATEGORY_II),
        ("inform", "serious", SaMDRiskCategory.CATEGORY_I),
        ("inform", "non_serious", SaMDRiskCategory.CATEGORY_I),
    ],
)
def test_risk_matrix(significance, situation, expected):
    classifier = SaMDClassifier()
    assert classifier.classify(significance, situation) == expected


def test_invalid_significance_raises():
    classifier = SaMDClassifier()
    with pytest.raises(ValueError):
        classifier.classify("nonsense", "critical")


def test_describe_returns_requirements():
    classifier = SaMDClassifier()
    info = classifier.describe(SaMDRiskCategory.CATEGORY_IV)
    assert info["requirements"]
    assert "level" in info
