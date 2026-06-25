import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "gaokao.db"

PROVINCE_CONFIGS = {
    "zhejiang": {
        "name": "浙江",
        "max_applications": 80,
        "application_unit": "major",
        "application_unit_label": "专业",
        "subject_model": "3+3",
        "subject_pool": ["物理", "化学", "生物", "政治", "历史", "地理", "技术"],
        "elective_count": 3,
        "score_range": (0, 750),
        "batches": ["普通类"],
    },
    "jiangsu": {
        "name": "江苏",
        "max_applications": 40,
        "application_unit": "major_group",
        "application_unit_label": "院校专业组",
        "subject_model": "3+1+2",
        "required_subject_category": True,
        "subject_categories": ["物理", "历史"],
        "subject_pool": ["化学", "生物", "政治", "地理"],
        "elective_count": 2,
        "majors_per_group": 6,
        "score_range": (0, 750),
        "batches": ["普通类"],
    },
    "shanghai": {
        "name": "上海",
        "max_applications": 24,
        "application_unit": "major_group",
        "application_unit_label": "院校专业组",
        "subject_model": "3+3",
        "subject_pool": ["物理", "化学", "生物", "政治", "历史", "地理"],
        "elective_count": 3,
        "majors_per_group": 4,
        "score_range": (0, 660),
        "batches": ["普通类"],
    },
}

RISK_TIERS = {
    "reach": {"label": "冲", "color": "#FF4B4B", "description": "冲刺，录取风险较高"},
    "slight_reach": {"label": "稳冲", "color": "#FFA500", "description": "有一定风险，但有机会"},
    "match": {"label": "稳", "color": "#00CC66", "description": "匹配度较好，录取概率较高"},
    "safe": {"label": "保", "color": "#4A90D9", "description": "较为安全，录取概率高"},
    "backup": {"label": "垫底", "color": "#999999", "description": "兜底选择，基本确保录取"},
}

TIER_DISTRIBUTION = {
    "zhejiang": {
        "aggressive": {"reach": (18, 22), "slight_reach": (10, 14), "match": (25, 30), "safe": (12, 16), "backup": (4, 6)},
        "balanced": {"reach": (15, 20), "slight_reach": (8, 10), "match": (30, 35), "safe": (20, 25), "backup": (5, 10)},
        "conservative": {"reach": (5, 10), "slight_reach": (5, 8), "match": (25, 30), "safe": (25, 30), "backup": (8, 12)},
    },
    "jiangsu": {
        "aggressive": {"reach": (8, 10), "slight_reach": (4, 6), "match": (12, 14), "safe": (8, 10), "backup": (2, 4)},
        "balanced": {"reach": (6, 8), "slight_reach": (3, 5), "match": (14, 16), "safe": (12, 14), "backup": (4, 6)},
        "conservative": {"reach": (2, 4), "slight_reach": (2, 4), "match": (12, 14), "safe": (14, 16), "backup": (6, 8)},
    },
    "shanghai": {
        "aggressive": {"reach": (5, 7), "slight_reach": (3, 4), "match": (7, 9), "safe": (4, 5), "backup": (1, 2)},
        "balanced": {"reach": (3, 5), "slight_reach": (2, 3), "match": (8, 10), "safe": (6, 8), "backup": (2, 3)},
        "conservative": {"reach": (1, 2), "slight_reach": (1, 2), "match": (7, 9), "safe": (8, 10), "backup": (3, 4)},
    },
}

STRATEGY_LABELS = {
    "aggressive": "冲刺型",
    "balanced": "均衡型",
    "conservative": "稳妥型",
}

MAJOR_CATEGORIES = [
    "计算机类", "电子信息类", "机械类", "土木建筑类", "经济金融类",
    "工商管理类", "法学类", "医学类", "教育学类", "文学类",
    "理学类", "农学类", "艺术类",
]

LLM_CONFIG = {
    "api_key": os.getenv("LLM_API_KEY", ""),
    "base_url": os.getenv("LLM_BASE_URL", "https://api.deepseek.com"),
    "model": os.getenv("LLM_MODEL", "deepseek-chat"),
    "mock_mode": os.getenv("LLM_MOCK_MODE", "true").lower() == "true",
}
