"""Fairness / bias metrics for ML model outputs.

Implements the common group-fairness metrics referenced by FDA's AI/ML SaMD
guidance and GMLP principle on evaluating performance across subgroups.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class MetricResult:
    metric_name: str
    metric_value: float  # disparity, in [0, 1]; 0 = perfectly fair
    threshold: float
    passes_threshold: bool
    subgroup_details: dict = field(default_factory=dict)


class BiasDetector:
    """Computes group-fairness disparity metrics across a protected attribute.

    Predictions and labels are treated as binary (0/1). Each metric returns a
    *disparity* in [0, 1] (max minus min across subgroups); lower is fairer. A
    metric passes when ``disparity <= 1 - threshold`` where ``threshold`` is the
    desired fairness ratio (default 0.8, the "four-fifths" rule).
    """

    def __init__(self, default_threshold: float = 0.8):
        self.default_threshold = default_threshold

    def demographic_parity(
        self, predictions: np.ndarray, protected: np.ndarray
    ) -> dict[str, float]:
        """Positive prediction rate P(Y_hat=1 | A=a) per subgroup."""
        rates: dict[str, float] = {}
        for group in np.unique(protected):
            mask = protected == group
            rates[str(group)] = float(np.mean(predictions[mask])) if mask.any() else 0.0
        return rates

    def equalized_odds(
        self, predictions: np.ndarray, labels: np.ndarray, protected: np.ndarray
    ) -> dict[str, dict[str, float]]:
        """True-positive and false-positive rate per subgroup."""
        out: dict[str, dict[str, float]] = {}
        for group in np.unique(protected):
            mask = protected == group
            y, yhat = labels[mask], predictions[mask]
            pos, neg = y == 1, y == 0
            tpr = float(np.mean(yhat[pos])) if pos.any() else 0.0
            fpr = float(np.mean(yhat[neg])) if neg.any() else 0.0
            out[str(group)] = {"tpr": tpr, "fpr": fpr}
        return out

    def predictive_parity(
        self, predictions: np.ndarray, labels: np.ndarray, protected: np.ndarray
    ) -> dict[str, float]:
        """Positive predictive value P(Y=1 | Y_hat=1, A=a) per subgroup."""
        ppv: dict[str, float] = {}
        for group in np.unique(protected):
            mask = protected == group
            yhat_pos = (predictions == 1) & mask
            ppv[str(group)] = (
                float(np.mean(labels[yhat_pos])) if yhat_pos.any() else 0.0
            )
        return ppv

    # -- aggregation ---------------------------------------------------------
    @staticmethod
    def _disparity(values: dict[str, float]) -> float:
        if not values:
            return 0.0
        vals = list(values.values())
        return float(max(vals) - min(vals))

    def assess_metric(
        self,
        metric_name: str,
        subgroup_values: dict[str, float],
        threshold: float | None = None,
    ) -> MetricResult:
        threshold = self.default_threshold if threshold is None else threshold
        disparity = self._disparity(subgroup_values)
        passes = disparity <= (1.0 - threshold)
        return MetricResult(
            metric_name=metric_name,
            metric_value=round(disparity, 4),
            threshold=threshold,
            passes_threshold=passes,
            subgroup_details={k: round(v, 4) for k, v in subgroup_values.items()},
        )

    def full_bias_audit(
        self,
        predictions: np.ndarray,
        protected_attributes: dict[str, np.ndarray],
        labels: np.ndarray | None = None,
        thresholds: dict[str, float] | None = None,
    ) -> list[tuple[str, MetricResult]]:
        """Run all applicable metrics for every protected attribute.

        Returns a list of ``(attribute_name, MetricResult)`` tuples. Metrics that
        require labels are skipped when ``labels`` is None.
        """
        thresholds = thresholds or {}
        results: list[tuple[str, MetricResult]] = []
        predictions = np.asarray(predictions)

        for attr_name, attr_values in protected_attributes.items():
            attr_values = np.asarray(attr_values)
            thr = thresholds.get(attr_name)

            dp = self.demographic_parity(predictions, attr_values)
            results.append(
                (attr_name, self.assess_metric("demographic_parity", dp, thr))
            )

            if labels is not None:
                labels = np.asarray(labels)
                eo = self.equalized_odds(predictions, labels, attr_values)
                tpr_values = {g: v["tpr"] for g, v in eo.items()}
                results.append(
                    (attr_name, self.assess_metric("equal_opportunity_tpr", tpr_values, thr))
                )
                pp = self.predictive_parity(predictions, labels, attr_values)
                results.append(
                    (attr_name, self.assess_metric("predictive_parity", pp, thr))
                )

        return results
