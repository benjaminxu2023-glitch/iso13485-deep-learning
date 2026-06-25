"""排名匹配引擎 — 基于省排名的志愿分层（纯数学，无LLM）"""

from __future__ import annotations

import statistics
from db.models import AdmissionRecord, RecommendationItem, CurrentYearPlan
from config.settings import RISK_TIERS


YEAR_WEIGHTS = {0: 0.50, 1: 0.30, 2: 0.20}


def _weighted_rank(history: list[AdmissionRecord]) -> float | None:
    sorted_history = sorted(history, key=lambda r: r.year, reverse=True)
    ranks = []
    for rec in sorted_history:
        if rec.min_rank is not None:
            ranks.append(rec.min_rank)

    if not ranks:
        return None

    if len(ranks) == 1:
        return float(ranks[0])

    total_weight = 0.0
    weighted_sum = 0.0
    for i, rank in enumerate(ranks):
        w = YEAR_WEIGHTS.get(i, 0.10)
        weighted_sum += rank * w
        total_weight += w

    return weighted_sum / total_weight


def _stability_score(history: list[AdmissionRecord]) -> float:
    ranks = [r.min_rank for r in history if r.min_rank is not None]
    if len(ranks) < 2:
        return 0.5
    mean = statistics.mean(ranks)
    if mean == 0:
        return 0.5
    cv = statistics.stdev(ranks) / mean
    if cv < 0.05:
        return 1.0
    elif cv < 0.10:
        return 0.8
    elif cv < 0.20:
        return 0.6
    else:
        return 0.3


def classify_tier(student_rank: int, weighted_historical_rank: float) -> tuple[str, str]:
    if weighted_historical_rank <= 0:
        return "match", "medium"

    ratio = student_rank / weighted_historical_rank

    if ratio > 1.15:
        return "reach", "high"
    elif ratio > 1.03:
        return "slight_reach", "medium_high"
    elif ratio >= 0.85:
        return "match", "medium"
    elif ratio >= 0.65:
        return "safe", "low"
    else:
        return "backup", "very_low"


def match_program(
    student_rank: int,
    plan: CurrentYearPlan,
    history: list[AdmissionRecord],
) -> RecommendationItem | None:
    w_rank = _weighted_rank(history)
    if w_rank is None:
        return None

    tier, risk_level = classify_tier(student_rank, w_rank)
    stability = _stability_score(history)

    historical_ranks = [r.min_rank for r in sorted(history, key=lambda r: r.year, reverse=True) if r.min_rank]
    historical_scores = [r.min_score for r in sorted(history, key=lambda r: r.year, reverse=True) if r.min_score]

    tier_info = RISK_TIERS[tier]
    reason_parts = [
        f"考生排名{student_rank}，近年录取排名加权平均{int(w_rank)}",
        f"分层: {tier_info['label']}（{tier_info['description']}）",
    ]
    if stability < 0.6:
        reason_parts.append("注意：该专业历年录取排名波动较大，预测可靠性较低")

    enrollment_change = ""
    if plan.enrollment_count and history:
        last_enrollment = history[0].enrollment_count
        if last_enrollment and plan.enrollment_count != last_enrollment:
            diff = plan.enrollment_count - last_enrollment
            direction = "增加" if diff > 0 else "减少"
            enrollment_change = f"今年招生计划{direction}{abs(diff)}人"
            reason_parts.append(enrollment_change)

    manual_items = []
    if plan.charter_special_conditions:
        manual_items.append(f"查看招生章程特殊条件: {plan.charter_special_conditions}")
    manual_items.append("核实当年招生计划")
    manual_items.append("确认校区和学费")

    evidence = f"历年最低录取排名: {historical_ranks}; 稳定性评分: {stability:.1f}"

    return RecommendationItem(
        university_name=plan.university_name,
        university_code=plan.university_code,
        major_name=plan.major_name,
        major_code=plan.major_code,
        major_group_code=plan.major_group_code,
        city=plan.city,
        campus=plan.campus,
        tuition=plan.tuition,
        subject_requirements=plan.subject_requirements,
        historical_min_ranks=historical_ranks,
        historical_min_scores=historical_scores,
        current_year_plan_count=plan.enrollment_count,
        tier=tier,
        risk_level=risk_level,
        reason="；".join(reason_parts),
        manual_review_items=manual_items,
        evidence=evidence,
    )
