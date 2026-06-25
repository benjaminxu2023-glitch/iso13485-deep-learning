"""江苏省种子数据生成器"""

import json
import random

random.seed(43)

UNIVERSITIES = [
    {"name": "南京大学", "code": "NJU_JS", "city": "南京", "tier": 1, "base_rank": 1000},
    {"name": "东南大学", "code": "SEU_JS", "city": "南京", "tier": 1, "base_rank": 4000},
    {"name": "南京航空航天大学", "code": "NUAA", "city": "南京", "tier": 2, "base_rank": 10000},
    {"name": "南京理工大学", "code": "NJUST", "city": "南京", "tier": 2, "base_rank": 12000},
    {"name": "河海大学", "code": "HHU", "city": "南京", "tier": 2, "base_rank": 15000},
    {"name": "苏州大学", "code": "SUDA", "city": "苏州", "tier": 2, "base_rank": 13000},
    {"name": "南京师范大学", "code": "NJNU", "city": "南京", "tier": 2, "base_rank": 16000},
    {"name": "江南大学", "code": "JIANGNAN", "city": "无锡", "tier": 3, "base_rank": 25000},
    {"name": "南京工业大学", "code": "NJTECH", "city": "南京", "tier": 3, "base_rank": 35000},
    {"name": "扬州大学", "code": "YZU", "city": "扬州", "tier": 3, "base_rank": 45000},
]

MAJOR_GROUPS = [
    {"group_code": "01", "category": "物理", "majors": [
        {"name": "计算机科学与技术", "code": "080901", "subjects": [], "rank_offset": 0, "tuition": 5800},
        {"name": "软件工程", "code": "080902", "subjects": [], "rank_offset": 500, "tuition": 5800},
        {"name": "电子信息工程", "code": "080701", "subjects": [], "rank_offset": 800, "tuition": 5800},
        {"name": "数学与应用数学", "code": "070101", "subjects": [], "rank_offset": 1000, "tuition": 5500},
        {"name": "机械工程", "code": "080201", "subjects": [], "rank_offset": 2000, "tuition": 5800},
        {"name": "土木工程", "code": "081001", "subjects": [], "rank_offset": 3000, "tuition": 5800},
    ]},
    {"group_code": "02", "category": "物理", "majors": [
        {"name": "临床医学", "code": "100201", "subjects": ["化学"], "rank_offset": -500, "tuition": 6800},
        {"name": "口腔医学", "code": "100301", "subjects": ["化学"], "rank_offset": -200, "tuition": 6800},
        {"name": "生物科学", "code": "071001", "subjects": ["化学"], "rank_offset": 3000, "tuition": 5500},
    ]},
    {"group_code": "03", "category": "历史", "majors": [
        {"name": "法学", "code": "030101", "subjects": [], "rank_offset": 1000, "tuition": 5200},
        {"name": "汉语言文学", "code": "050101", "subjects": [], "rank_offset": 1500, "tuition": 5200},
        {"name": "英语", "code": "050201", "subjects": [], "rank_offset": 2000, "tuition": 5200},
        {"name": "会计学", "code": "120203", "subjects": [], "rank_offset": 1200, "tuition": 5200},
    ]},
]

YEARS = [2022, 2023, 2024]


def _rank_to_score(rank: int) -> int:
    if rank <= 1000:
        return random.randint(650, 670)
    elif rank <= 5000:
        return random.randint(620, 650)
    elif rank <= 15000:
        return random.randint(590, 620)
    elif rank <= 30000:
        return random.randint(560, 590)
    elif rank <= 50000:
        return random.randint(530, 560)
    else:
        return random.randint(500, 530)


def generate_history() -> list[dict]:
    records = []
    for uni in UNIVERSITIES:
        for group in MAJOR_GROUPS:
            for major in group["majors"]:
                for year in YEARS:
                    base = uni["base_rank"] + major["rank_offset"]
                    drift = random.randint(-int(base * 0.07), int(base * 0.07))
                    min_rank = max(1, base + drift)
                    records.append({
                        "province": "jiangsu",
                        "year": year,
                        "university_name": uni["name"],
                        "university_code": uni["code"],
                        "major_name": major["name"],
                        "major_code": major["code"],
                        "major_group_code": f"{uni['code']}_{group['group_code']}",
                        "batch": "普通类",
                        "plan_type": "major_group",
                        "enrollment_count": random.choice([3, 5, 8, 10, 15]),
                        "min_score": _rank_to_score(min_rank),
                        "min_rank": min_rank,
                        "avg_score": _rank_to_score(min_rank) + random.randint(1, 5),
                        "avg_rank": max(1, min_rank - random.randint(50, 300)),
                        "subject_requirements": json.dumps(major["subjects"], ensure_ascii=False),
                        "subject_category": group["category"],
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
                    "province": "jiangsu",
                    "year": 2025,
                    "university_name": uni["name"],
                    "university_code": uni["code"],
                    "major_name": major["name"],
                    "major_code": major["code"],
                    "major_group_code": f"{uni['code']}_{group['group_code']}",
                    "batch": "普通类",
                    "plan_type": "major_group",
                    "enrollment_count": random.choice([3, 5, 8, 10, 15]),
                    "subject_requirements": json.dumps(major["subjects"], ensure_ascii=False),
                    "subject_category": group["category"],
                    "tuition": major["tuition"],
                    "city": uni["city"],
                    "campus": "主校区",
                    "charter_special_conditions": None,
                    "remarks": None,
                })
    return plans


def generate_charter_audits() -> list[dict]:
    return []
