"""资格筛选Agent — 过滤不符合条件的志愿"""

from __future__ import annotations

from db.models import StudentProfile, CurrentYearPlan
from agents.rule_engine.base import BaseRuleEngine


def filter_eligible(
    student: StudentProfile,
    plans: list[CurrentYearPlan],
    rule_engine: BaseRuleEngine,
) -> tuple[list[CurrentYearPlan], list[dict]]:
    eligible = []
    filtered_out = []

    for plan in plans:
        result = rule_engine.check_eligibility(student, plan)
        if result.eligible:
            eligible.append(plan)
        else:
            filtered_out.append({
                "university": plan.university_name,
                "major": plan.major_name,
                "reason": result.reason,
            })

    return eligible, filtered_out
