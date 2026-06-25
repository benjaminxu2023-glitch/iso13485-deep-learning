from __future__ import annotations

import json
import sqlite3
from typing import Optional

from db.models import AdmissionRecord, CurrentYearPlan


def get_admission_history(
    conn: sqlite3.Connection,
    province: str,
    years: Optional[list[int]] = None,
    university_code: Optional[str] = None,
) -> list[AdmissionRecord]:
    query = "SELECT * FROM admission_history WHERE province = ?"
    params: list = [province]
    if years:
        placeholders = ",".join("?" * len(years))
        query += f" AND year IN ({placeholders})"
        params.extend(years)
    if university_code:
        query += " AND university_code = ?"
        params.append(university_code)
    query += " ORDER BY year DESC, university_name, major_name"
    rows = conn.execute(query, params).fetchall()
    return [AdmissionRecord(**dict(row)) for row in rows]


def get_current_year_plans(
    conn: sqlite3.Connection,
    province: str,
) -> list[CurrentYearPlan]:
    query = """SELECT * FROM admission_plan_current_year
               WHERE province = ? ORDER BY university_name, major_name"""
    rows = conn.execute(query, [province]).fetchall()
    return [CurrentYearPlan(**dict(row)) for row in rows]


def get_history_for_program(
    conn: sqlite3.Connection,
    province: str,
    university_code: str,
    major_code: str,
) -> list[AdmissionRecord]:
    query = """SELECT * FROM admission_history
               WHERE province = ? AND university_code = ? AND major_code = ?
               ORDER BY year DESC"""
    rows = conn.execute(query, [province, university_code, major_code]).fetchall()
    return [AdmissionRecord(**dict(row)) for row in rows]


def get_charter_risks(
    conn: sqlite3.Connection,
    university_code: str,
    province: str,
) -> list[dict]:
    row = conn.execute(
        "SELECT risk_items FROM charter_audit WHERE university_code = ? AND province = ?",
        [university_code, province],
    ).fetchone()
    if row:
        return json.loads(row["risk_items"])
    return []


def save_cache(
    conn: sqlite3.Connection,
    session_id: str,
    stage: str,
    input_hash: str,
    result: str,
) -> None:
    conn.execute(
        """INSERT OR REPLACE INTO recommendation_cache
           (session_id, stage, input_hash, result) VALUES (?, ?, ?, ?)""",
        [session_id, stage, input_hash, result],
    )
    conn.commit()


def get_cache(
    conn: sqlite3.Connection,
    session_id: str,
    stage: str,
    input_hash: str,
) -> Optional[str]:
    row = conn.execute(
        """SELECT result FROM recommendation_cache
           WHERE session_id = ? AND stage = ? AND input_hash = ?""",
        [session_id, stage, input_hash],
    ).fetchone()
    return row["result"] if row else None
