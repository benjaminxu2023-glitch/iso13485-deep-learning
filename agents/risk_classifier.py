"""风险分级Agent — 综合评估每个志愿的风险等级"""

from __future__ import annotations

from db.models import RecommendationItem, RiskItem


def classify_risks(
    recommendations: list[RecommendationItem],
    charter_risks: dict[str, list[RiskItem]],
) -> list[RecommendationItem]:
    for rec in recommendations:
        key = rec.university_code or rec.university_name
        if key in charter_risks:
            rec.charter_risks = charter_risks[key]

        high_count = sum(1 for r in rec.charter_risks if r.severity == "high")
        medium_count = sum(1 for r in rec.charter_risks if r.severity == "medium")

        if rec.tier in ("reach",) or high_count > 0:
            rec.risk_level = "high"
        elif rec.tier in ("slight_reach",) or medium_count > 1:
            rec.risk_level = "medium_high"
        elif rec.tier in ("match",):
            rec.risk_level = "medium" if medium_count > 0 else "medium"
        elif rec.tier in ("safe",):
            rec.risk_level = "low"
        else:
            rec.risk_level = "very_low"

    return recommendations
