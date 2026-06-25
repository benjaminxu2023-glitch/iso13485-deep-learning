"""浙江省种子数据生成器 — 20所大学、~200个专业、3年历史数据"""

import json
import random

random.seed(42)

UNIVERSITIES = [
    {"name": "浙江大学", "code": "ZJU", "city": "杭州", "tier": 1, "base_rank": 800},
    {"name": "复旦大学", "code": "FDU", "city": "上海", "tier": 1, "base_rank": 600},
    {"name": "上海交通大学", "code": "SJTU", "city": "上海", "tier": 1, "base_rank": 650},
    {"name": "南京大学", "code": "NJU", "city": "南京", "tier": 1, "base_rank": 1200},
    {"name": "中国科学技术大学", "code": "USTC", "city": "合肥", "tier": 1, "base_rank": 1500},
    {"name": "同济大学", "code": "TJU", "city": "上海", "tier": 2, "base_rank": 3500},
    {"name": "东南大学", "code": "SEU", "city": "南京", "tier": 2, "base_rank": 5000},
    {"name": "华东师范大学", "code": "ECNU", "city": "上海", "tier": 2, "base_rank": 6000},
    {"name": "浙江工业大学", "code": "ZJUT", "city": "杭州", "tier": 3, "base_rank": 30000},
    {"name": "杭州电子科技大学", "code": "HDU", "city": "杭州", "tier": 3, "base_rank": 35000},
    {"name": "浙江师范大学", "code": "ZJNU", "city": "金华", "tier": 3, "base_rank": 45000},
    {"name": "宁波大学", "code": "NBU", "city": "宁波", "tier": 3, "base_rank": 40000},
    {"name": "浙江理工大学", "code": "ZSTU", "city": "杭州", "tier": 3, "base_rank": 42000},
    {"name": "杭州师范大学", "code": "HZNU", "city": "杭州", "tier": 4, "base_rank": 60000},
    {"name": "浙江农林大学", "code": "ZAFU", "city": "杭州", "tier": 4, "base_rank": 70000},
    {"name": "温州大学", "code": "WZU", "city": "温州", "tier": 4, "base_rank": 75000},
    {"name": "浙江财经大学", "code": "ZUFE", "city": "杭州", "tier": 3, "base_rank": 38000},
    {"name": "浙江工商大学", "code": "ZJGSU", "city": "杭州", "tier": 3, "base_rank": 40000},
    {"name": "中国计量大学", "code": "CJLU", "city": "杭州", "tier": 4, "base_rank": 55000},
    {"name": "浙江中医药大学", "code": "ZCMU", "city": "杭州", "tier": 4, "base_rank": 50000},
]

MAJORS = [
    {"name": "计算机科学与技术", "code": "080901", "category": "计算机类",
     "subjects": ["物理"], "rank_offset": 0, "tuition": 5500,
     "charter": "色盲色弱不宜报考"},
    {"name": "软件工程", "code": "080902", "category": "计算机类",
     "subjects": ["物理"], "rank_offset": 500, "tuition": 5500,
     "charter": None},
    {"name": "电子信息工程", "code": "080701", "category": "电子信息类",
     "subjects": ["物理"], "rank_offset": 1000, "tuition": 5500,
     "charter": None},
    {"name": "临床医学", "code": "100201", "category": "医学类",
     "subjects": ["物理", "化学"], "rank_offset": -500, "tuition": 6500,
     "charter": "色盲色弱限报；身高男165cm以上，女155cm以上"},
    {"name": "口腔医学", "code": "100301", "category": "医学类",
     "subjects": ["物理", "化学"], "rank_offset": -200, "tuition": 6500,
     "charter": "色盲色弱限报；左利手不宜报考"},
    {"name": "金融学", "code": "020301", "category": "经济金融类",
     "subjects": [], "rank_offset": 800, "tuition": 5000,
     "charter": None},
    {"name": "会计学", "code": "120203", "category": "工商管理类",
     "subjects": [], "rank_offset": 1500, "tuition": 5000,
     "charter": None},
    {"name": "法学", "code": "030101", "category": "法学类",
     "subjects": [], "rank_offset": 2000, "tuition": 5000,
     "charter": None},
    {"name": "机械工程", "code": "080201", "category": "机械类",
     "subjects": ["物理"], "rank_offset": 3000, "tuition": 5500,
     "charter": None},
    {"name": "土木工程", "code": "081001", "category": "土木建筑类",
     "subjects": ["物理"], "rank_offset": 4000, "tuition": 5500,
     "charter": "色盲不宜报考"},
    {"name": "英语", "code": "050201", "category": "文学类",
     "subjects": [], "rank_offset": 2500, "tuition": 5000,
     "charter": "英语单科成绩不低于120分"},
    {"name": "数学与应用数学", "code": "070101", "category": "理学类",
     "subjects": ["物理"], "rank_offset": 1200, "tuition": 5000,
     "charter": None},
    {"name": "生物科学", "code": "071001", "category": "理学类",
     "subjects": ["化学", "生物"], "rank_offset": 5000, "tuition": 5000,
     "charter": "色盲色弱限报"},
    {"name": "汉语言文学", "code": "050101", "category": "文学类",
     "subjects": [], "rank_offset": 3000, "tuition": 5000,
     "charter": None},
    {"name": "电气工程及其自动化", "code": "080601", "category": "电子信息类",
     "subjects": ["物理"], "rank_offset": 600, "tuition": 5500,
     "charter": "色盲不宜报考"},
]

YEARS = [2022, 2023, 2024]


def _rank_to_score(rank: int) -> int:
    if rank <= 500:
        return random.randint(680, 700)
    elif rank <= 2000:
        return random.randint(660, 680)
    elif rank <= 5000:
        return random.randint(640, 660)
    elif rank <= 10000:
        return random.randint(620, 640)
    elif rank <= 20000:
        return random.randint(600, 620)
    elif rank <= 40000:
        return random.randint(570, 600)
    elif rank <= 60000:
        return random.randint(545, 570)
    elif rank <= 80000:
        return random.randint(520, 545)
    else:
        return random.randint(490, 520)


def generate_history() -> list[dict]:
    records = []
    for uni in UNIVERSITIES:
        available_majors = MAJORS if uni["tier"] <= 2 else random.sample(MAJORS, k=min(10, len(MAJORS)))
        for major in available_majors:
            for year in YEARS:
                base = uni["base_rank"] + major["rank_offset"]
                year_drift = random.randint(-int(base * 0.08), int(base * 0.08))
                min_rank = max(1, base + year_drift)
                min_score = _rank_to_score(min_rank)
                avg_rank = max(1, min_rank - random.randint(100, 500))
                avg_score = min_score + random.randint(1, 5)
                enrollment = random.choice([2, 3, 4, 5, 6, 8, 10, 15, 20, 30])
                records.append({
                    "province": "zhejiang",
                    "year": year,
                    "university_name": uni["name"],
                    "university_code": uni["code"],
                    "major_name": major["name"],
                    "major_code": major["code"],
                    "major_group_code": None,
                    "batch": "普通类",
                    "plan_type": "major",
                    "enrollment_count": enrollment,
                    "min_score": min_score,
                    "min_rank": min_rank,
                    "avg_score": avg_score,
                    "avg_rank": avg_rank,
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
        available_majors = MAJORS if uni["tier"] <= 2 else random.sample(MAJORS, k=min(10, len(MAJORS)))
        for major in available_majors:
            enrollment = random.choice([2, 3, 4, 5, 6, 8, 10, 15, 20, 30])
            plans.append({
                "province": "zhejiang",
                "year": 2025,
                "university_name": uni["name"],
                "university_code": uni["code"],
                "major_name": major["name"],
                "major_code": major["code"],
                "major_group_code": None,
                "batch": "普通类",
                "plan_type": "major",
                "enrollment_count": enrollment,
                "subject_requirements": json.dumps(major["subjects"], ensure_ascii=False),
                "subject_category": None,
                "tuition": major["tuition"],
                "city": uni["city"],
                "campus": "主校区",
                "charter_special_conditions": major["charter"],
                "remarks": None,
            })
    return plans


def generate_charter_audits() -> list[dict]:
    audits = []
    for uni in UNIVERSITIES:
        risk_items = []
        available_majors = MAJORS if uni["tier"] <= 2 else random.sample(MAJORS, k=min(10, len(MAJORS)))
        for major in available_majors:
            if major["charter"]:
                risk_items.append({
                    "risk_type": "体检限制" if "色盲" in major["charter"] or "身高" in major["charter"] else "单科成绩",
                    "detail": f"{major['name']}: {major['charter']}",
                    "severity": "high" if "限报" in major["charter"] else "medium",
                })
        if risk_items:
            audits.append({
                "university_code": uni["code"],
                "university_name": uni["name"],
                "province": "zhejiang",
                "risk_items": json.dumps(risk_items, ensure_ascii=False),
                "audit_source": "招生章程",
            })
    return audits
