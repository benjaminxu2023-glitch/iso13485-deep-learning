import pytest
from agents.rule_engine import get_rule_engine
from db.models import StudentProfile, CurrentYearPlan


@pytest.fixture
def zj_engine():
    return get_rule_engine("zhejiang")


@pytest.fixture
def js_engine():
    return get_rule_engine("jiangsu")


@pytest.fixture
def sh_engine():
    return get_rule_engine("shanghai")


def test_zhejiang_max_apps(zj_engine):
    assert zj_engine.get_max_applications() == 80


def test_jiangsu_max_apps(js_engine):
    assert js_engine.get_max_applications() == 40


def test_shanghai_max_apps(sh_engine):
    assert sh_engine.get_max_applications() == 24


def test_zhejiang_subject_match_physics(zj_engine):
    student = StudentProfile(province="zhejiang", score=600, rank=10000, subjects=["物理", "化学", "生物"])
    plan = CurrentYearPlan(province="zhejiang", university_name="测试大学", major_name="计算机",
                           subject_requirements=["物理"])
    result = zj_engine.check_subject_match(student, plan)
    assert result.eligible


def test_zhejiang_subject_no_requirement(zj_engine):
    student = StudentProfile(province="zhejiang", score=600, rank=10000, subjects=["历史", "政治", "地理"])
    plan = CurrentYearPlan(province="zhejiang", university_name="测试大学", major_name="法学",
                           subject_requirements=[])
    result = zj_engine.check_subject_match(student, plan)
    assert result.eligible


def test_zhejiang_subject_mismatch(zj_engine):
    student = StudentProfile(province="zhejiang", score=600, rank=10000, subjects=["历史", "政治", "地理"])
    plan = CurrentYearPlan(province="zhejiang", university_name="测试大学", major_name="计算机",
                           subject_requirements=["物理"])
    result = zj_engine.check_subject_match(student, plan)
    assert not result.eligible


def test_jiangsu_category_mismatch(js_engine):
    student = StudentProfile(province="jiangsu", score=600, rank=10000,
                             subject_category="历史", subjects=["政治", "地理"])
    plan = CurrentYearPlan(province="jiangsu", university_name="测试大学", major_name="计算机",
                           subject_category="物理", subject_requirements=[])
    result = js_engine.check_subject_match(student, plan)
    assert not result.eligible


def test_jiangsu_category_match(js_engine):
    student = StudentProfile(province="jiangsu", score=600, rank=10000,
                             subject_category="物理", subjects=["化学", "生物"])
    plan = CurrentYearPlan(province="jiangsu", university_name="测试大学", major_name="计算机",
                           subject_category="物理", subject_requirements=[])
    result = js_engine.check_subject_match(student, plan)
    assert result.eligible


def test_eligibility_budget_filter(zj_engine):
    student = StudentProfile(province="zhejiang", score=600, rank=10000,
                             subjects=["物理", "化学", "生物"], budget_limit=6000)
    plan = CurrentYearPlan(province="zhejiang", university_name="测试大学", major_name="计算机",
                           subject_requirements=["物理"], tuition=8000)
    result = zj_engine.check_eligibility(student, plan)
    assert not result.eligible


def test_eligibility_rejected_major(zj_engine):
    student = StudentProfile(province="zhejiang", score=600, rank=10000,
                             subjects=["物理", "化学", "生物"], rejected_majors=["土木工程"])
    plan = CurrentYearPlan(province="zhejiang", university_name="测试大学", major_name="土木工程",
                           subject_requirements=["物理"])
    result = zj_engine.check_eligibility(student, plan)
    assert not result.eligible


def test_gradient_warning_too_many_reach(zj_engine):
    tier_counts = {"reach": 30, "slight_reach": 10, "match": 20, "safe": 15, "backup": 5}
    warnings = zj_engine.check_gradient(tier_counts)
    assert any("冲刺" in w for w in warnings)


def test_gradient_warning_insufficient_backup(zj_engine):
    tier_counts = {"reach": 10, "match": 50, "safe": 18, "backup": 2}
    warnings = zj_engine.check_gradient(tier_counts)
    assert any("垫底" in w for w in warnings)
