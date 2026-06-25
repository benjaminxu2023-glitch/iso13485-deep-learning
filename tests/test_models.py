import pytest
from db.models import StudentProfile


def test_valid_zhejiang_student():
    s = StudentProfile(
        province="zhejiang", score=620, rank=18000,
        subjects=["物理", "化学", "生物"],
    )
    assert s.province == "zhejiang"
    assert len(s.subjects) == 3


def test_valid_jiangsu_student():
    s = StudentProfile(
        province="jiangsu", score=610, rank=15000,
        subject_category="物理", subjects=["化学", "生物"],
    )
    assert s.subject_category == "物理"
    assert len(s.subjects) == 2


def test_valid_shanghai_student():
    s = StudentProfile(
        province="shanghai", score=550, rank=5000,
        subjects=["物理", "化学", "生物"],
    )
    assert s.score <= 660


def test_invalid_province():
    with pytest.raises(ValueError, match="不支持的省份"):
        StudentProfile(province="beijing", score=600, rank=10000, subjects=["物理", "化学", "生物"])


def test_zhejiang_wrong_subject_count():
    with pytest.raises(ValueError):
        StudentProfile(province="zhejiang", score=600, rank=10000, subjects=["物理", "化学"])


def test_jiangsu_missing_category():
    with pytest.raises(ValueError, match="首选科目"):
        StudentProfile(province="jiangsu", score=600, rank=10000, subjects=["化学", "生物"])


def test_jiangsu_wrong_elective():
    with pytest.raises(ValueError):
        StudentProfile(province="jiangsu", score=600, rank=10000,
                       subject_category="物理", subjects=["化学", "技术"])


def test_shanghai_score_over_660():
    with pytest.raises(ValueError):
        StudentProfile(province="shanghai", score=700, rank=100, subjects=["物理", "化学", "生物"])


def test_invalid_risk_preference():
    with pytest.raises(ValueError, match="风险偏好"):
        StudentProfile(province="zhejiang", score=600, rank=10000,
                       subjects=["物理", "化学", "生物"], risk_preference="yolo")


def test_all_subjects_zhejiang():
    s = StudentProfile(province="zhejiang", score=600, rank=10000, subjects=["物理", "化学", "生物"])
    all_subj = s.all_subjects()
    assert "语文" in all_subj
    assert "数学" in all_subj
    assert "英语" in all_subj
    assert "物理" in all_subj
    assert len(all_subj) == 6


def test_all_subjects_jiangsu():
    s = StudentProfile(province="jiangsu", score=600, rank=10000,
                       subject_category="物理", subjects=["化学", "生物"])
    all_subj = s.all_subjects()
    assert "物理" in all_subj
    assert len(all_subj) == 6
