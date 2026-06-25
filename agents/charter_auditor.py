"""招生章程审核Agent — 审查隐藏风险（LLM增强）"""

from __future__ import annotations

import json
from db.models import RecommendationItem, RiskItem
from agents import llm_client

SYSTEM_PROMPT = """你是高考招生章程审核员。分析以下院校的招生章程特殊条件，识别潜在风险。
重点关注：
1. 体检限制（色盲、色弱、视力、身高等）
2. 单科成绩要求
3. 外语语种要求
4. 学费和中外合作办学
5. 校区位置
6. 专业分流规则
7. 转专业政策
8. 调剂范围
返回JSON格式：{"risk_items": [{"risk_type": "...", "detail": "...", "severity": "high/medium/low"}]}"""


def audit_charters(
    recommendations: list[RecommendationItem],
) -> dict[str, list[RiskItem]]:
    results: dict[str, list[RiskItem]] = {}

    universities_seen = set()
    for rec in recommendations:
        key = rec.university_code or rec.university_name
        if key in universities_seen:
            continue
        universities_seen.add(key)

        charter_conditions = []
        for r in recommendations:
            rkey = r.university_code or r.university_name
            if rkey == key and r.manual_review_items:
                for item in r.manual_review_items:
                    if "章程" in item:
                        charter_conditions.append(item)

        if not charter_conditions:
            continue

        user_msg = json.dumps({
            "university": rec.university_name,
            "conditions": charter_conditions,
        }, ensure_ascii=False)

        try:
            response = llm_client.chat(SYSTEM_PROMPT, user_msg)
            data = json.loads(response)
            risk_items = [RiskItem(**item) for item in data.get("risk_items", [])]
            if risk_items:
                results[key] = risk_items
        except Exception:
            pass

    return results
