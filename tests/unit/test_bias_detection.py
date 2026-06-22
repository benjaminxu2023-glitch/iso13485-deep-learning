"""Tests for the fairness/bias metrics."""

from __future__ import annotations

import numpy as np

from iso13485_audit.ml_validation.bias_detection import BiasDetector


def test_demographic_parity_perfectly_fair():
    detector = BiasDetector()
    preds = np.array([1, 0, 1, 0])
    protected = np.array(["A", "A", "B", "B"])
    rates = detector.demographic_parity(preds, protected)
    assert rates["A"] == 0.5
    assert rates["B"] == 0.5
    metric = detector.assess_metric("demographic_parity", rates)
    assert metric.metric_value == 0.0
    assert metric.passes_threshold


def test_demographic_parity_detects_disparity():
    detector = BiasDetector()
    preds = np.array([1, 1, 0, 0])
    protected = np.array(["A", "A", "B", "B"])
    rates = detector.demographic_parity(preds, protected)
    metric = detector.assess_metric("demographic_parity", rates)
    assert metric.metric_value == 1.0
    assert not metric.passes_threshold


def test_equalized_odds_tpr_fpr():
    detector = BiasDetector()
    preds = np.array([1, 0, 1, 1, 0, 1])
    labels = np.array([1, 1, 0, 1, 1, 0])
    protected = np.array(["A", "A", "A", "B", "B", "B"])
    eo = detector.equalized_odds(preds, labels, protected)
    assert set(eo.keys()) == {"A", "B"}
    assert "tpr" in eo["A"] and "fpr" in eo["A"]


def test_full_audit_skips_label_metrics_without_labels():
    detector = BiasDetector()
    preds = np.array([1, 0, 1, 0])
    protected = {"sex": np.array(["M", "M", "F", "F"])}
    results = detector.full_bias_audit(preds, protected, labels=None)
    metric_names = {m.metric_name for _, m in results}
    assert metric_names == {"demographic_parity"}


def test_full_audit_with_labels_runs_all_metrics():
    detector = BiasDetector()
    preds = np.array([1, 0, 1, 0, 1, 1])
    labels = np.array([1, 0, 0, 0, 1, 1])
    protected = {"sex": np.array(["M", "M", "M", "F", "F", "F"])}
    results = detector.full_bias_audit(preds, protected, labels=labels)
    metric_names = {m.metric_name for _, m in results}
    assert "demographic_parity" in metric_names
    assert "equal_opportunity_tpr" in metric_names
    assert "predictive_parity" in metric_names
