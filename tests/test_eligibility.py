import pytest
from agents.eligibility import filter_eligible
from agents.rule_engine import get_rule_engine
from db.models import StudentProfile, CurrentYearPlan


def test_filter_by_subject():
    student = StudentProfile(
        province="zhejiang", score=600, rank=10000,
        subjects=["历史", "政治", "地理"],
    )
    engine = get_rule_engine("zhejiang")
    plans = [
        CurrentYearPlan(province="zhejiang", university_name="A大学", major_name="计算机",
                        subject_requirements=["物理"]),
        CurrentYearPlan(province="zhejiang", university_name="B大学", major_name="法学",
                        subject_requirements=[]),
        CurrentYearPlan(province="zhejiang", university_name="C大学", major_name="历史学",
                        subject_requirements=["历史"]),
    ]

    eligible, filtered = filter_eligible(student, plans, engine)
    assert len(eligible) == 2
    assert len(filtered) == 1
    assert filtered[0]["major"] == "计算机"


def test_filter_all_eligible():
    student = StudentProfile(
        province="zhejiang", score=600, rank=10000,
        subjects=["物理", "化学", "生物"],
    )
    engine = get_rule_engine("zhejiang")
    plans = [
        CurrentYearPlan(province="zhejiang", university_name="A大学", major_name="计算机",
                        subject_requirements=["物理"]),
        CurrentYearPlan(province="zhejiang", university_name="B大学", major_name="金融",
                        subject_requirements=[]),
    ]

    eligible, filtered = filter_eligible(student, plans, engine)
    assert len(eligible) == 2
    assert len(filtered) == 0
