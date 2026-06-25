#!/usr/bin/env python3
"""快速查询 — 输入分数，直接输出志愿建议"""

import argparse
import sys
from collections import Counter

from config.settings import PROVINCE_CONFIGS, RISK_TIERS, TIER_DISTRIBUTION, STRATEGY_LABELS
from db.connection import get_db
from db.models import StudentProfile
from db.repository import get_current_year_plans, get_admission_history
from agents.rule_engine import get_rule_engine
from agents.eligibility import filter_eligible
from agents.rank_matcher import match_program


TIER_ORDER = ["reach", "slight_reach", "match", "safe", "backup"]


def select_by_distribution(all_recs, dist):
    by_tier = {}
    for rec in all_recs:
        by_tier.setdefault(rec.tier, []).append(rec)
    selected = []
    for tier in TIER_ORDER:
        low, high = dist.get(tier, (0, 0))
        available = by_tier.get(tier, [])
        target = min(high, len(available))
        target = max(target, min(low, len(available)))
        selected.extend(available[:target])
    return selected


def print_header(text):
    width = 60
    print()
    print("=" * width)
    print(f"  {text}")
    print("=" * width)


def print_recommendations(recs, strategy_label):
    if not recs:
        print("  （无推荐）")
        return

    tier_counts = Counter(r.tier for r in recs)
    tier_summary = " | ".join(
        f"{RISK_TIERS[t]['label']}{tier_counts.get(t, 0)}"
        for t in TIER_ORDER if tier_counts.get(t, 0) > 0
    )
    print(f"  分布: {tier_summary}  共{len(recs)}个志愿")
    print("-" * 60)

    current_tier = None
    for i, rec in enumerate(recs, 1):
        tier_info = RISK_TIERS.get(rec.tier, {"label": rec.tier})
        if rec.tier != current_tier:
            current_tier = rec.tier
            print(f"\n  ── {tier_info['label']}（{tier_info['description']}） ──")

        ranks_str = " → ".join(str(r) for r in rec.historical_min_ranks) if rec.historical_min_ranks else "无数据"
        tuition_str = f"{rec.tuition}元" if rec.tuition else "待确认"
        print(f"  {i:>3}. {rec.university_name} — {rec.major_name}")
        print(f"       城市: {rec.city or '未知'}  学费: {tuition_str}  今年计划: {rec.current_year_plan_count or '?'}人")
        print(f"       历年最低排名: {ranks_str}")
        if rec.manual_review_items:
            for item in rec.manual_review_items:
                if "特殊条件" in item:
                    print(f"       ⚠ {item}")


def run(province, score, rank, subjects, subject_category=None, strategy="balanced"):
    cfg = PROVINCE_CONFIGS[province]

    profile_data = {
        "province": province,
        "score": score,
        "rank": rank,
        "subjects": subjects,
        "subject_category": subject_category,
        "preferred_cities": [],
        "preferred_majors": [],
        "rejected_majors": [],
        "budget_limit": None,
        "accept_adjustment": True,
        "accept_sino_foreign": False,
        "risk_preference": strategy,
        "health_limits": None,
        "career_direction": None,
    }
    student = StudentProfile(**profile_data)

    conn = get_db()
    rule_engine = get_rule_engine(province)

    if not rule_engine.validate_subjects(student):
        print(f"错误: 选科组合不符合{cfg['name']}的要求")
        conn.close()
        return

    plans = get_current_year_plans(conn, province)
    if not plans:
        print(f"错误: 未找到{cfg['name']}的招生计划数据")
        conn.close()
        return

    eligible_plans, filtered_out = filter_eligible(student, plans, rule_engine)

    history = get_admission_history(conn, province)
    conn.close()

    history_by_key = {}
    for rec in history:
        key = f"{rec.university_code}_{rec.major_code}"
        history_by_key.setdefault(key, []).append(rec)

    recommendations = []
    for plan in eligible_plans:
        key = f"{plan.university_code}_{plan.major_code}"
        plan_history = history_by_key.get(key, [])
        if not plan_history:
            continue
        rec = match_program(student.rank, plan, plan_history)
        if rec:
            recommendations.append(rec)

    recommendations.sort(key=lambda r: TIER_ORDER.index(r.tier) if r.tier in TIER_ORDER else 5)

    print_header(f"志愿质检员 — {cfg['name']}高考志愿建议")
    all_subjects = subjects if province != "jiangsu" else [subject_category] + subjects
    print(f"  分数: {score}  排名: {rank}  选科: {', '.join(all_subjects)}")
    print(f"  符合条件的专业: {len(eligible_plans)}  有历史数据的: {len(recommendations)}")

    distributions = TIER_DISTRIBUTION.get(province, TIER_DISTRIBUTION["zhejiang"])

    for st_type in ("aggressive", "balanced", "conservative"):
        dist = distributions[st_type]
        strategy_recs = select_by_distribution(recommendations, dist)
        print_header(f"{STRATEGY_LABELS[st_type]}（{len(strategy_recs)}个志愿）")
        print_recommendations(strategy_recs, STRATEGY_LABELS[st_type])

    print()
    print("=" * 60)
    print("  ⚠️ 本系统仅提供参考，最终以各省教育考试院官方信息为准")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="高考志愿快速查询")
    parser.add_argument("--province", "-p", required=True,
                        choices=["zhejiang", "jiangsu", "shanghai"],
                        help="省份: zhejiang / jiangsu / shanghai")
    parser.add_argument("--score", "-s", type=int, required=True, help="高考分数")
    parser.add_argument("--rank", "-r", type=int, required=True, help="省排名（位次）")
    parser.add_argument("--subjects", "-j", nargs="+", required=True,
                        help="选考科目（空格分隔），如: 物理 化学 生物")
    parser.add_argument("--category", "-c", default=None,
                        help="江苏首选科目: 物理 or 历史（仅江苏需要）")
    parser.add_argument("--strategy", default="balanced",
                        choices=["aggressive", "balanced", "conservative"],
                        help="策略偏好: aggressive/balanced/conservative (default: balanced)")

    args = parser.parse_args()

    if args.province == "jiangsu" and not args.category:
        print("错误: 江苏考生必须指定 --category (物理 或 历史)")
        sys.exit(1)

    run(args.province, args.score, args.rank, args.subjects,
        subject_category=args.category, strategy=args.strategy)


if __name__ == "__main__":
    main()
