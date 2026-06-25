"""初始化数据库并插入种子数据"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from db.connection import init_db, get_db
from data.seed_zhejiang import generate_history as zj_history, generate_current_year_plans as zj_plans, generate_charter_audits as zj_charters
from data.seed_jiangsu import generate_history as js_history, generate_current_year_plans as js_plans, generate_charter_audits as js_charters
from data.seed_shanghai import generate_history as sh_history, generate_current_year_plans as sh_plans, generate_charter_audits as sh_charters


def _insert_records(conn, table, records):
    if not records:
        return
    columns = records[0].keys()
    placeholders = ", ".join("?" * len(columns))
    col_str = ", ".join(columns)
    sql = f"INSERT OR IGNORE INTO {table} ({col_str}) VALUES ({placeholders})"
    for rec in records:
        conn.execute(sql, list(rec.values()))
    conn.commit()


def main():
    print("初始化数据库...")
    init_db()

    conn = get_db()

    print("插入浙江数据...")
    _insert_records(conn, "admission_history", zj_history())
    _insert_records(conn, "admission_plan_current_year", zj_plans())
    _insert_records(conn, "charter_audit", zj_charters())
    zj_count = conn.execute("SELECT COUNT(*) FROM admission_history WHERE province='zhejiang'").fetchone()[0]
    print(f"  浙江历史数据: {zj_count}条")

    print("插入江苏数据...")
    _insert_records(conn, "admission_history", js_history())
    _insert_records(conn, "admission_plan_current_year", js_plans())
    _insert_records(conn, "charter_audit", js_charters())
    js_count = conn.execute("SELECT COUNT(*) FROM admission_history WHERE province='jiangsu'").fetchone()[0]
    print(f"  江苏历史数据: {js_count}条")

    print("插入上海数据...")
    _insert_records(conn, "admission_history", sh_history())
    _insert_records(conn, "admission_plan_current_year", sh_plans())
    _insert_records(conn, "charter_audit", sh_charters())
    sh_count = conn.execute("SELECT COUNT(*) FROM admission_history WHERE province='shanghai'").fetchone()[0]
    print(f"  上海历史数据: {sh_count}条")

    plan_count = conn.execute("SELECT COUNT(*) FROM admission_plan_current_year").fetchone()[0]
    charter_count = conn.execute("SELECT COUNT(*) FROM charter_audit").fetchone()[0]
    print(f"\n当年招生计划: {plan_count}条")
    print(f"章程审核记录: {charter_count}条")
    print("数据库初始化完成!")

    conn.close()


if __name__ == "__main__":
    main()
