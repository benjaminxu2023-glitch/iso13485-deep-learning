"""最终审核Agent — 审查志愿表的整体合理性"""

from __future__ import annotations

import json
from collections import Counter

from db.models import StudentProfile, StrategyPlan, AuditResult
from agents.rule_engine.base import BaseRuleEngine
from agents import llm_client

SYSTEM_PROMPT = """你是高考志愿填报最终审核员。审查整份志愿表，识别问题和风险。
审核项目：
1. 选科要求是否匹配
2. 冲刺志愿是否过多
3. 保底志愿是否充足
4. 志愿梯度是否合理
5. 热门专业是否过于集中
6. 学费风险
7. 校区风险
8. 体检限制风险
9. 调剂风险
返回JSON格式：{"status": "pass/warning/high_risk/invalid", "issues": [...], "warnings": [...], "high_risks": [...]}"""


def audit_strategy(
    student: StudentProfile,
    strategy: StrategyPlan,
    rule_engine: BaseRuleEngine,
) -> AuditResult:
    issues = []
    warnings = []
    high_risks = []

    tier_counts = Counter(r.tier for r in strategy.recommendations)

    gradient_warnings = rule_engine.check_gradient(tier_counts)
    warnings.extend(gradient_warnings)

    total = len(strategy.recommendations)
    if total == 0:
        return AuditResult(status="invalid", issues=["无可推荐志愿"])

    major_counts = Counter(r.major_name for r in strategy.recommendations)
    popular_majors = [m for m, c in major_counts.items() if c > total * 0.2]
    if popular_majors:
        warnings.append(f"以下专业志愿过于集中: {', '.join(popular_majors)}")

    city_counts = Counter(r.city for r in strategy.recommendations if r.city)
    if len(city_counts) == 1:
        warnings.append(f"所有志愿集中在{list(city_counts.keys())[0]}一个城市")

    for rec in strategy.recommendations:
        for risk in rec.charter_risks:
            if risk.severity == "high":
                high_risks.append(f"{rec.university_name}-{rec.major_name}: {risk.detail}")

    if not student.accept_adjustment:
        warnings.append("考生不接受专业调剂，滑档风险显著增加")

    user_msg = json.dumps({
        "strategy_type": strategy.strategy_type,
        "total": total,
        "tier_distribution": dict(tier_counts),
        "high_risks_count": len(high_risks),
        "warnings_count": len(warnings),
    }, ensure_ascii=False)

    try:
        response = llm_client.chat(SYSTEM_PROMPT, user_msg)
        data = json.loads(response)
        issues.extend(data.get("issues", []))
        warnings.extend(data.get("warnings", []))
        high_risks.extend(data.get("high_risks", []))
        llm_status = data.get("status", "warning")
    except Exception:
        llm_status = "warning"

    if high_risks:
        status = "high_risk"
    elif warnings:
        status = "warning"
    elif issues:
        status = "warning"
    else:
        status = "pass"

    return AuditResult(
        status=status,
        issues=issues,
        warnings=warnings,
        high_risks=high_risks,
    )
