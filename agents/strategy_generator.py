"""填报策略生成Agent — 生成冲刺/均衡/稳妥三种方案"""

from __future__ import annotations

import json
from collections import Counter

from config.settings import TIER_DISTRIBUTION, STRATEGY_LABELS
from db.models import StudentProfile, RecommendationItem, StrategyPlan
from agents import llm_client

SYSTEM_PROMPT = """你是高考志愿填报策略分析师。根据考生信息和推荐志愿列表，生成填报策略总结。
要求：
1. 分析志愿梯度是否合理
2. 评估整体风险水平
3. 给出改进建议
返回JSON格式：{"summary": "...", "overall_risk": "...", "suggestions": [...]}"""

TIER_ORDER = ["reach", "slight_reach", "match", "safe", "backup"]


def generate_strategies(
    student: StudentProfile,
    recommendations: list[RecommendationItem],
) -> list[StrategyPlan]:
    province = student.province
    distributions = TIER_DISTRIBUTION.get(province, TIER_DISTRIBUTION["zhejiang"])

    strategies = []
    for strategy_type in ("aggressive", "balanced", "conservative"):
        dist = distributions[strategy_type]
        strategy_recs = _select_by_distribution(recommendations, dist)
        tier_counts = Counter(r.tier for r in strategy_recs)

        user_msg = json.dumps({
            "strategy_type": strategy_type,
            "student_rank": student.rank,
            "student_score": student.score,
            "total_recommendations": len(strategy_recs),
            "tier_distribution": dict(tier_counts),
        }, ensure_ascii=False)

        try:
            response = llm_client.chat(SYSTEM_PROMPT, user_msg)
            data = json.loads(response)
            summary = data.get("summary", "")
            overall_risk = data.get("overall_risk", "中等")
        except Exception:
            summary = f"{STRATEGY_LABELS[strategy_type]}策略，共{len(strategy_recs)}个志愿"
            overall_risk = "中等"

        strategies.append(StrategyPlan(
            strategy_type=strategy_type,
            strategy_label=STRATEGY_LABELS[strategy_type],
            recommendations=strategy_recs,
            tier_distribution=dict(tier_counts),
            overall_risk=overall_risk,
            summary=summary,
        ))

    return strategies


def _select_by_distribution(
    all_recs: list[RecommendationItem],
    dist: dict[str, tuple[int, int]],
) -> list[RecommendationItem]:
    by_tier: dict[str, list[RecommendationItem]] = {}
    for rec in all_recs:
        by_tier.setdefault(rec.tier, []).append(rec)

    selected: list[RecommendationItem] = []
    for tier in TIER_ORDER:
        low, high = dist.get(tier, (0, 0))
        available = by_tier.get(tier, [])
        target = min(high, len(available))
        target = max(target, min(low, len(available)))
        selected.extend(available[:target])

    return selected
