"""学生画像Agent — 解析和验证用户输入"""

from __future__ import annotations

from db.models import StudentProfile


def parse_student_input(form_data: dict) -> StudentProfile:
    return StudentProfile(**form_data)
