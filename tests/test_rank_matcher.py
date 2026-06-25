import pytest
from agents.rank_matcher import classify_tier, match_program
from db.models import AdmissionRecord, CurrentYearPlan


def test_classify_reach():
    tier, risk = classify_tier(student_rank=25000, weighted_historical_rank=18000)
    assert tier == "reach"
    assert risk == "high"


def test_classify_match():
    tier, risk = classify_tier(student_rank=18000, weighted_historical_rank=18000)
    assert tier == "match"


def test_classify_safe():
    tier, risk = classify_tier(student_rank=12000, weighted_historical_rank=18000)
    assert tier == "safe"


def test_classify_backup():
    tier, risk = classify_tier(student_rank=8000, weighted_historical_rank=18000)
    assert tier == "backup"


def test_classify_slight_reach():
    tier, risk = classify_tier(student_rank=19500, weighted_historical_rank=18000)
    assert tier == "slight_reach"


def test_match_program_basic():
    plan = CurrentYearPlan(
        province="zhejiang",
        university_name="浙江工业大学",
        university_code="ZJUT",
        major_name="计算机科学与技术",
        major_code="080901",
        enrollment_count=30,
        tuition=5500,
        city="杭州",
    )
    history = [
        AdmissionRecord(province="zhejiang", year=2024, university_name="浙江工业大学",
                        university_code="ZJUT", major_name="计算机科学与技术", major_code="080901",
                        min_rank=30000, min_score=580),
        AdmissionRecord(province="zhejiang", year=2023, university_name="浙江工业大学",
                        university_code="ZJUT", major_name="计算机科学与技术", major_code="080901",
                        min_rank=31000, min_score=575),
        AdmissionRecord(province="zhejiang", year=2022, university_name="浙江工业大学",
                        university_code="ZJUT", major_name="计算机科学与技术", major_code="080901",
                        min_rank=29000, min_score=582),
    ]

    result = match_program(student_rank=20000, plan=plan, history=history)
    assert result is not None
    assert result.tier == "safe"
    assert result.university_name == "浙江工业大学"


def test_match_program_reach():
    plan = CurrentYearPlan(
        province="zhejiang",
        university_name="浙江大学",
        university_code="ZJU",
        major_name="计算机科学与技术",
        major_code="080901",
    )
    history = [
        AdmissionRecord(province="zhejiang", year=2024, university_name="浙江大学",
                        university_code="ZJU", major_name="计算机科学与技术", major_code="080901",
                        min_rank=800, min_score=690),
    ]

    result = match_program(student_rank=20000, plan=plan, history=history)
    assert result is not None
    assert result.tier == "reach"


def test_match_program_no_history():
    plan = CurrentYearPlan(
        province="zhejiang",
        university_name="新大学",
        major_name="新专业",
    )
    result = match_program(student_rank=20000, plan=plan, history=[])
    assert result is None
