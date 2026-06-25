"""上海市种子数据生成器"""

import json
import random

random.seed(44)

UNIVERSITIES = [
    {"name": "复旦大学", "code": "FDU_SH", "city": "上海", "tier": 1, "base_rank": 500},
    {"name": "上海交通大学", "code": "SJTU_SH", "city": "上海", "tier": 1, "base_rank": 550},
    {"name": "同济大学", "code": "TJU_SH", "city": "上海", "tier": 1, "base_rank": 2500},
    {"name": "华东师范大学", "code": "ECNU_SH", "city": "上海", "tier": 2, "base_rank": 4000},
    {"name": "上海财经大学", "code": "SUFE", "city": "上海", "tier": 2, "base_rank": 3500},
    {"name": "华东理工大学", "code": "ECUST", "city": "上海", "tier": 2, "base_rank": 6000},
    {"name": "上海大学", "code": "SHU", "city": "上海", "tier": 3, "base_rank": 9000},
    {"name": "上海理工大学", "code": "USST", "city": "上海", "tier": 3, "base_rank": 14000},
    {"name": "上海师范大学", "code": "SHNU", "city": "上海", "tier": 3, "base_rank": 16000},
    {"name": "上海海事大学", "code": "SMU", "city": "上海", "tier": 4, "base_rank": 20000},
]

MAJOR_GROUPS = [
    {"group_code": "01", "majors": [
        {"name": "计算机科学与技术", "code": "080901", "subjects": ["物理"], "rank_offset": 0, "tuition": 5000},
        {"name": "软件工程", "code": "080902", "subjects": ["物理"], "rank_offset": 300, "tuition": 5000},
        {"name": "电子信息工程", "code": "080701", "subjects": ["物理"], "rank_offset": 500, "tuition": 5000},
        {"name": "数学与应用数学", "code": "070101", "subjects": ["物理"], "rank_offset": 800, "tuition": 5000},
    ]},
    {"group_code": "02", "majors": [
        {"name": "金融学", "code": "020301", "subjects": [], "rank_offset": 200, "tuition": 5000},
        {"name": "会计学", "code": "120203", "subjects": [], "rank_offset": 600, "tuition": 5000},
        {"name": "法学", "code": "030101", "subjects": [], "rank_offset": 1000, "tuition": 5000},
        {"name": "英语", "code": "050201", "subjects": [], "rank_offset": 1200, "tuition": 5000},
    ]},
    {"group_code": "03", "majors": [
        {"name": "临床医学", "code": "100201", "subjects": ["物理", "化学"], "rank_offset": -300, "tuition": 6500},
        {"name": "口腔医学", "code": "100301", "subjects": ["物理", "化学"], "rank_offset": 0, "tuition": 6500},
        {"name": "生物科学", "code": "071001", "subjects": ["化学"], "rank_offset": 2000, "tuition": 5000},
        {"name": "化学", "code": "070301", "subjects": ["化学"], "rank_offset": 2500, "tuition": 5000},
    ]},
]

YEARS = [2022, 2023, 2024]


def _rank_to_score(rank: int) -> int:
    if rank <= 500:
        return random.randint(580, 600)
    elif rank <= 2000:
        return random.randint(560, 580)
    elif rank <= 5000:
        return random.randint(540, 560)
    elif rank <= 10000:
        return random.randint(515, 540)
    elif rank <= 20000:
        return random.randint(490, 515)
    else:
        return random.randint(460, 490)


def generate_history() -> list[dict]:
    records = []
    for uni in UNIVERSITIES:
        for group in MAJOR_GROUPS:
            for major in group["majors"]:
                for year in YEARS:
                    base = uni["base_rank"] + major["rank_offset"]
                    drift = random.randint(-int(max(base, 1) * 0.06), int(max(base, 1) * 0.06))
                    min_rank = max(1, base + drift)
                    records.append({
                        "province": "shanghai",
                        "year": year,
                        "university_name": uni["name"],
                        "university_code": uni["code"],
                        "major_name": major["name"],
                        "major_code": major["code"],
                        "major_group_code": f"{uni['code']}_{group['group_code']}",
                        "batch": "普通类",
                        "plan_type": "major_group",
                        "enrollment_count": random.choice([2, 3, 4, 5, 8]),
                        "min_score": _rank_to_score(min_rank),
                        "min_rank": min_rank,
                        "avg_score": _rank_to_score(min_rank) + random.randint(1, 3),
                        "avg_rank": max(1, min_rank - random.randint(30, 200)),
                        "subject_requirements": json.dumps(major["subjects"], ensure_ascii=False),
                        "subject_category": None,
                        "city": uni["city"],
                        "campus": "主校区",
                        "tuition": major["tuition"],
                        "remarks": None,
                    })
    return records


def generate_current_year_plans() -> list[dict]:
    plans = []
    for uni in UNIVERSITIES:
        for group in MAJOR_GROUPS:
            for major in group["majors"]:
                plans.append({
                    "province": "shanghai",
                    "year": 2025,
                    "university_name": uni["name"],
                    "university_code": uni["code"],
                    "major_name": major["name"],
                    "major_code": major["code"],
                    "major_group_code": f"{uni['code']}_{group['group_code']}",
                    "batch": "普通类",
                    "plan_type": "major_group",
                    "enrollment_count": random.choice([2, 3, 4, 5, 8]),
                    "subject_requirements": json.dumps(major["subjects"], ensure_ascii=False),
                    "subject_category": None,
                    "tuition": major["tuition"],
                    "city": uni["city"],
                    "campus": "主校区",
                    "charter_special_conditions": None,
                    "remarks": None,
                })
    return plans


def generate_charter_audits() -> list[dict]:
    return []
