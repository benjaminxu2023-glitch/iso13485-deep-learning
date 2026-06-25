from __future__ import annotations

from config.settings import PROVINCE_CONFIGS
from db.models import StudentProfile, CurrentYearPlan
from agents.rule_engine.base import BaseRuleEngine, EligibilityResult


class ZhejiangRuleEngine(BaseRuleEngine):

    def __init__(self):
        self.config = PROVINCE_CONFIGS["zhejiang"]

    def get_province(self) -> str:
        return "zhejiang"

    def get_max_applications(self) -> int:
        return self.config["max_applications"]

    def get_application_unit(self) -> str:
        return self.config["application_unit"]

    def validate_subjects(self, student: StudentProfile) -> bool:
        if len(student.subjects) != self.config["elective_count"]:
            return False
        return all(s in self.config["subject_pool"] for s in student.subjects)

    def check_subject_match(self, student: StudentProfile, plan: CurrentYearPlan) -> EligibilityResult:
        required = plan.subject_requirements
        if not required:
            return EligibilityResult(True, "该专业不限选考科目")
        student_subjects = set(student.subjects)
        required_set = set(required)
        if student_subjects & required_set:
            matched = student_subjects & required_set
            return EligibilityResult(True, f"选考科目匹配: {', '.join(matched)}")
        return EligibilityResult(
            False,
            f"选考科目不匹配，要求{required}中至少一门，考生选考{student.subjects}"
        )

    def check_eligibility(self, student: StudentProfile, plan: CurrentYearPlan) -> EligibilityResult:
        subject_result = self.check_subject_match(student, plan)
        if not subject_result.eligible:
            return subject_result

        if not student.accept_sino_foreign and plan.tuition and plan.tuition > 15000:
            return EligibilityResult(False, f"学费{plan.tuition}元/年，疑似中外合作项目，考生不接受")

        if student.budget_limit and plan.tuition and plan.tuition > student.budget_limit:
            return EligibilityResult(False, f"学费{plan.tuition}元超出预算{student.budget_limit}元")

        if plan.major_name in student.rejected_majors:
            return EligibilityResult(False, f"考生排除了专业: {plan.major_name}")

        return EligibilityResult(True, "符合报考条件")

    def validate_application_count(self, count: int) -> bool:
        return 1 <= count <= self.config["max_applications"]

    def check_gradient(self, tier_counts: dict[str, int]) -> list[str]:
        warnings = []
        total = sum(tier_counts.values())

        reach = tier_counts.get("reach", 0) + tier_counts.get("slight_reach", 0)
        safe = tier_counts.get("safe", 0) + tier_counts.get("backup", 0)

        if reach > total * 0.35:
            warnings.append(f"冲刺志愿占比过高({reach}/{total})，建议不超过35%")
        if safe < total * 0.15:
            warnings.append(f"保底志愿不足({safe}/{total})，建议至少15%")
        if tier_counts.get("backup", 0) < 3:
            warnings.append("垫底志愿少于3个，存在滑档风险")
        if tier_counts.get("match", 0) < total * 0.3:
            warnings.append(f"稳妥志愿偏少({tier_counts.get('match', 0)}/{total})，建议占30%以上")
        return warnings
