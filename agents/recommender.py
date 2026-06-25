"""院校专业推荐Agent — 基于排名匹配结果生成推荐理由（LLM增强）"""

from __future__ import annotations

import json
from db.models import RecommendationItem, StudentProfile
from agents import llm_client

SYSTEM_PROMPT = """你是高考志愿填报质检员。根据考生信息和匹配结果，为每个推荐志愿生成推荐理由。
要求：
1. 理由必须包含数据依据（排名、分数）
2. 指出该志愿的优势和风险
3. 给出是否需要人工复核的建议
返回JSON格式：{"recommendations": [{"reason": "...", "additional_risks": [...], "suggestion": "..."}]}"""


def enhance_recommendations(
    student: StudentProfile,
    recommendations: list[RecommendationItem],
) -> list[RecommendationItem]:
    if not recommendations:
        return recommendations

    batch_size = 10
    enhanced = []

    for i in range(0, len(recommendations), batch_size):
        batch = recommendations[i:i + batch_size]
        batch_info = []
        for rec in batch:
            batch_info.append({
                "university": rec.university_name,
                "major": rec.major_name,
                "tier": rec.tier,
                "historical_ranks": rec.historical_min_ranks,
                "student_rank": student.rank,
            })

        user_msg = json.dumps({
            "student": {
                "province": student.province,
                "score": student.score,
                "rank": student.rank,
                "subjects": student.all_subjects(),
                "preferred_majors": student.preferred_majors,
                "preferred_cities": student.preferred_cities,
            },
            "batch": batch_info,
        }, ensure_ascii=False)

        try:
            response = llm_client.chat(SYSTEM_PROMPT, user_msg)
            data = json.loads(response)
            llm_recs = data.get("recommendations", [])

            for j, rec in enumerate(batch):
                if j < len(llm_recs):
                    llm_rec = llm_recs[j]
                    if llm_rec.get("reason"):
                        rec.reason = rec.reason + "；" + llm_rec["reason"]
                    for risk in llm_rec.get("additional_risks", []):
                        rec.manual_review_items.append(risk)
                enhanced.append(rec)
        except Exception:
            enhanced.extend(batch)

    return enhanced
