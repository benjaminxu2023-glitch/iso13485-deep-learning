"""GMLP model lifecycle stage-gate tracking."""

from __future__ import annotations

from ..models.ml_audit import MLModelLifecycleStage

# Ordered lifecycle stages and the artifacts expected to complete each one,
# aligned with FDA/IMDRF Good Machine Learning Practice (GMLP) principles.
STAGE_ORDER: list[MLModelLifecycleStage] = [
    MLModelLifecycleStage.PLANNING,
    MLModelLifecycleStage.DATA_COLLECTION,
    MLModelLifecycleStage.DEVELOPMENT,
    MLModelLifecycleStage.VERIFICATION,
    MLModelLifecycleStage.VALIDATION,
    MLModelLifecycleStage.DEPLOYMENT,
    MLModelLifecycleStage.MONITORING,
    MLModelLifecycleStage.RETIREMENT,
]

REQUIRED_ARTIFACTS: dict[str, list[str]] = {
    "planning": ["intended_use", "risk_analysis", "data_requirements"],
    "data_collection": ["dataset_description", "labeling_protocol", "demographics_summary"],
    "development": ["architecture_doc", "training_config", "hyperparameters"],
    "verification": ["unit_tests", "integration_tests", "performance_benchmarks"],
    "validation": ["clinical_validation_protocol", "validation_results", "bias_assessment"],
    "deployment": ["deployment_plan", "monitoring_plan", "rollback_plan"],
    "monitoring": ["performance_logs", "drift_reports", "incident_process"],
    "retirement": ["decommission_plan", "data_retention_record"],
}


class ModelLifecycleTracker:
    """Reports lifecycle status and required artifacts for an ML model."""

    def completed_stages(self, current: MLModelLifecycleStage) -> list[str]:
        idx = STAGE_ORDER.index(current)
        return [s.value for s in STAGE_ORDER[:idx]]

    def next_stage(self, current: MLModelLifecycleStage) -> str | None:
        idx = STAGE_ORDER.index(current)
        if idx + 1 < len(STAGE_ORDER):
            return STAGE_ORDER[idx + 1].value
        return None

    def required_artifacts(self, current: MLModelLifecycleStage) -> dict[str, list[str]]:
        """Return required artifacts for the current stage and all prior stages."""
        idx = STAGE_ORDER.index(current)
        relevant = STAGE_ORDER[: idx + 1]
        return {s.value: REQUIRED_ARTIFACTS.get(s.value, []) for s in relevant}

    def readiness_notes(
        self, model_record_fields: dict, current: MLModelLifecycleStage
    ) -> list[str]:
        """Heuristic readiness notes based on which model fields are populated."""
        notes: list[str] = []
        if not model_record_fields.get("intended_use"):
            notes.append("Intended use statement is missing (required from planning stage).")
        if not model_record_fields.get("samd_risk_category"):
            notes.append("SaMD risk category has not been assigned.")
        stage_idx = STAGE_ORDER.index(current)
        if stage_idx >= STAGE_ORDER.index(MLModelLifecycleStage.VALIDATION):
            if not model_record_fields.get("has_validation"):
                notes.append("No validation record found, but stage is at/after validation.")
            if not model_record_fields.get("has_bias_assessment"):
                notes.append("No bias assessment found; required for validation of SaMD.")
        if stage_idx >= STAGE_ORDER.index(MLModelLifecycleStage.DEPLOYMENT):
            if not model_record_fields.get("predetermined_change_control_plan"):
                notes.append(
                    "No Predetermined Change Control Plan (PCCP) for an adaptive model."
                )
        if not notes:
            notes.append("No blocking issues detected for the current stage.")
        return notes
