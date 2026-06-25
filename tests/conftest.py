import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from db.connection import init_db, get_db
from data.seed_zhejiang import generate_history, generate_current_year_plans, generate_charter_audits


@pytest.fixture
def db_conn():
    conn = get_db(":memory:")
    schema_path = Path(__file__).parent.parent / "db" / "schema.sql"
    conn.executescript(schema_path.read_text())

    history = generate_history()
    plans = generate_current_year_plans()
    charters = generate_charter_audits()

    for table, records in [
        ("admission_history", history),
        ("admission_plan_current_year", plans),
        ("charter_audit", charters),
    ]:
        if not records:
            continue
        columns = records[0].keys()
        placeholders = ", ".join("?" * len(columns))
        col_str = ", ".join(columns)
        sql = f"INSERT OR IGNORE INTO {table} ({col_str}) VALUES ({placeholders})"
        for rec in records:
            conn.execute(sql, list(rec.values()))
    conn.commit()

    yield conn
    conn.close()


@pytest.fixture
def zhejiang_student():
    from db.models import StudentProfile
    return StudentProfile(
        province="zhejiang",
        score=620,
        rank=18000,
        subjects=["物理", "化学", "生物"],
        preferred_cities=["杭州", "上海", "南京"],
        preferred_majors=["计算机类", "电子信息类"],
        risk_preference="balanced",
        accept_adjustment=True,
    )


@pytest.fixture
def jiangsu_student():
    from db.models import StudentProfile
    return StudentProfile(
        province="jiangsu",
        score=610,
        rank=15000,
        subject_category="物理",
        subjects=["化学", "生物"],
        preferred_cities=["南京", "苏州"],
        risk_preference="balanced",
        accept_adjustment=True,
    )
