"""流水线编排器 — 串联所有Agent，管理状态和缓存"""

from __future__ import annotations

import hashlib
import json
import sqlite3

from db.models import StudentProfile, PipelineResult, RecommendationItem
from db.repository import get_admission_history, get_current_year_plans, get_history_for_program
from agents.rule_engine import get_rule_engine
from agents.eligibility import filter_eligible
from agents.rank_matcher import match_program
from agents.recommender import enhance_recommendations
from agents.charter_auditor import audit_charters
from agents.risk_classifier import classify_risks
from agents.strategy_generator import generate_strategies
from agents.final_auditor import audit_strategy


def run_pipeline(
    student: StudentProfile,
    conn: sqlite3.Connection,
) -> PipelineResult:
    rule_engine = get_rule_engine(student.province)

    if not rule_engine.validate_subjects(student):
        raise ValueError(f"选科组合不符合{student.province}的要求")

    plans = get_current_year_plans(conn, student.province)
    if not plans:
        raise ValueError(f"未找到{student.province}的当年招生计划数据")

    eligible_plans, filtered_out = filter_eligible(student, plans, rule_engine)
    if not eligible_plans:
        raise ValueError("经过筛选后没有符合条件的志愿，请调整筛选条件")

    history = get_admission_history(conn, student.province)
    history_by_key: dict[str, list] = {}
    for rec in history:
        key = f"{rec.university_code}_{rec.major_code}"
        history_by_key.setdefault(key, []).append(rec)

    recommendations: list[RecommendationItem] = []
    for plan in eligible_plans:
        key = f"{plan.university_code}_{plan.major_code}"
        plan_history = history_by_key.get(key, [])
        if not plan_history:
            continue
        rec = match_program(student.rank, plan, plan_history)
        if rec:
            recommendations.append(rec)

    if not recommendations:
        raise ValueError("没有找到匹配的历史数据来生成推荐")

    recommendations.sort(key=lambda r: _tier_sort_key(r.tier))

    recommendations = enhance_recommendations(student, recommendations)

    charter_risks = audit_charters(recommendations)

    recommendations = classify_risks(recommendations, charter_risks)

    strategies = generate_strategies(student, recommendations)

    audit_result = None
    for strategy in strategies:
        if strategy.strategy_type == "balanced":
            audit_result = audit_strategy(student, strategy, rule_engine)
            break
    if audit_result is None and strategies:
        audit_result = audit_strategy(student, strategies[0], rule_engine)

    return PipelineResult(
        student=student,
        strategies=strategies,
        audit_result=audit_result,
        charter_risks={k: v for k, v in charter_risks.items()},
        all_recommendations=recommendations,
    )


def _tier_sort_key(tier: str) -> int:
    order = {"reach": 0, "slight_reach": 1, "match": 2, "safe": 3, "backup": 4}
    return order.get(tier, 5)
