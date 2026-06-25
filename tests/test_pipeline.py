import pytest
import os

os.environ["LLM_MOCK_MODE"] = "true"


def test_full_pipeline_zhejiang(db_conn, zhejiang_student):
    from pipeline.orchestrator import run_pipeline

    result = run_pipeline(zhejiang_student, db_conn)

    assert result is not None
    assert result.student.province == "zhejiang"
    assert len(result.all_recommendations) > 0
    assert len(result.strategies) == 3
    assert result.audit_result is not None

    strategy_types = {s.strategy_type for s in result.strategies}
    assert strategy_types == {"aggressive", "balanced", "conservative"}

    for rec in result.all_recommendations:
        assert rec.tier in ("reach", "slight_reach", "match", "safe", "backup")
        assert rec.university_name
        assert rec.major_name
        assert rec.reason


def test_pipeline_no_plans(db_conn):
    from db.models import StudentProfile
    from pipeline.orchestrator import run_pipeline

    student = StudentProfile(
        province="zhejiang", score=620, rank=18000,
        subjects=["物理", "化学", "生物"],
    )

    db_conn.execute("DELETE FROM admission_plan_current_year WHERE province='zhejiang'")
    db_conn.commit()

    with pytest.raises(ValueError, match="招生计划"):
        run_pipeline(student, db_conn)
