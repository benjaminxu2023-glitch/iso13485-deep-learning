"""离线选校工具生成器 — 读取DB数据，注入HTML模板，生成可离线使用的单文件HTML"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from config.settings import PROVINCE_CONFIGS, RISK_TIERS, TIER_DISTRIBUTION
from db.repository import get_current_year_plans, get_admission_history


TEMPLATE_PATH = Path(__file__).parent / "templates" / "select_tool.html"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "选校工具_江浙沪.html"


def _build_program_data(conn: sqlite3.Connection, province: str) -> list[dict]:
    plans = get_current_year_plans(conn, province)
    history = get_admission_history(conn, province)

    history_map: dict[str, list] = {}
    for rec in history:
        key = (rec.university_code or "") + "_" + (rec.major_code or "")
        history_map.setdefault(key, []).append(rec)

    programs = []
    for plan in plans:
        key = (plan.university_code or "") + "_" + (plan.major_code or "")
        hist = history_map.get(key, [])
        hist_sorted = sorted(hist, key=lambda r: r.year, reverse=True)

        min_ranks = [r.min_rank for r in hist_sorted if r.min_rank is not None]
        min_scores = [r.min_score for r in hist_sorted if r.min_score is not None]

        programs.append({
            "university_name": plan.university_name,
            "university_code": plan.university_code or "",
            "major_name": plan.major_name,
            "major_code": plan.major_code or "",
            "major_group_code": plan.major_group_code or "",
            "city": plan.city or "",
            "campus": plan.campus or "",
            "tuition": plan.tuition,
            "enrollment_count": plan.enrollment_count,
            "subject_requirements": plan.subject_requirements,
            "subject_category": plan.subject_category or "",
            "charter_special_conditions": plan.charter_special_conditions or "",
            "historical_min_ranks": min_ranks,
            "historical_min_scores": min_scores,
        })

    return programs


def _build_province_config(province: str) -> dict:
    cfg = PROVINCE_CONFIGS[province]
    return {
        "name": cfg["name"],
        "max_applications": cfg["max_applications"],
        "application_unit": cfg["application_unit"],
        "subject_model": cfg["subject_model"],
        "subject_pool": cfg["subject_pool"],
        "elective_count": cfg["elective_count"],
        "score_range": list(cfg["score_range"]),
    }


def _build_tier_distribution() -> dict:
    result = {}
    for province, strategies in TIER_DISTRIBUTION.items():
        result[province] = {}
        for strategy, tiers in strategies.items():
            result[province][strategy] = {
                tier: list(range_tuple) for tier, range_tuple in tiers.items()
            }
    return result


def generate(conn: sqlite3.Connection, output_path: Path | None = None) -> Path:
    output = output_path or OUTPUT_PATH

    app_data = {
        "programs": {},
        "province_configs": {},
        "risk_tiers": RISK_TIERS,
        "tier_distribution": _build_tier_distribution(),
    }

    for province in ("zhejiang", "jiangsu", "shanghai"):
        app_data["programs"][province] = _build_program_data(conn, province)
        app_data["province_configs"][province] = _build_province_config(province)

    data_json = json.dumps(app_data, ensure_ascii=False, separators=(",", ":"))

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    html = template.replace("/*__APP_DATA__*/null", data_json)

    output.write_text(html, encoding="utf-8")
    return output


def main():
    from db.connection import get_db
    conn = get_db()
    path = generate(conn)
    conn.close()

    data_check = path.read_text(encoding="utf-8")
    start = data_check.find("var APP_DATA = ") + len("var APP_DATA = ")
    end = data_check.find(";\n\nvar state", start)
    blob = data_check[start:end]
    parsed = json.loads(blob)
    for prov in ("zhejiang", "jiangsu", "shanghai"):
        count = len(parsed["programs"][prov])
        print(f"  {prov}: {count} programs")
    print(f"Generated: {path}")
    print(f"File size: {path.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
