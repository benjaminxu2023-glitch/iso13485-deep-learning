"""统一LLM客户端 — 默认DeepSeek，支持模拟模式"""

from __future__ import annotations

import json
import os
from typing import Optional

from config.settings import LLM_CONFIG

_client = None


def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI
        _client = OpenAI(
            api_key=LLM_CONFIG["api_key"],
            base_url=LLM_CONFIG["base_url"],
        )
    return _client


def chat(
    system_prompt: str,
    user_message: str,
    temperature: float = 0.3,
    json_mode: bool = True,
) -> str:
    if LLM_CONFIG["mock_mode"]:
        return _mock_response(system_prompt, user_message)

    client = _get_client()
    kwargs = {
        "model": LLM_CONFIG["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": temperature,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


def _mock_response(system_prompt: str, user_message: str) -> str:
    if "推荐理由" in system_prompt or "recommendation" in system_prompt.lower():
        return json.dumps({
            "recommendations": [
                {
                    "reason": "该专业历年录取排名与考生排名匹配度较高，且专业方向符合考生兴趣",
                    "additional_risks": [],
                    "suggestion": "建议关注该校今年的招生计划变化",
                }
            ]
        }, ensure_ascii=False)

    if "章程" in system_prompt or "charter" in system_prompt.lower():
        return json.dumps({
            "risk_items": [
                {"risk_type": "体检限制", "detail": "部分专业对色盲色弱有限制", "severity": "medium"},
                {"risk_type": "单科成绩", "detail": "英语专业要求英语单科不低于120分", "severity": "medium"},
            ]
        }, ensure_ascii=False)

    if "策略" in system_prompt or "strategy" in system_prompt.lower():
        return json.dumps({
            "summary": "根据考生成绩和偏好，建议采用均衡型填报策略，兼顾冲刺与保底",
            "overall_risk": "中等",
            "suggestions": [
                "适当增加稳妥志愿比例",
                "注意专业梯度分布",
                "关注招生章程中的特殊要求",
            ],
        }, ensure_ascii=False)

    if "审核" in system_prompt or "audit" in system_prompt.lower():
        return json.dumps({
            "status": "warning",
            "issues": [],
            "warnings": ["建议增加保底志愿数量", "部分志愿集中在热门专业，存在扎堆风险"],
            "high_risks": [],
        }, ensure_ascii=False)

    return json.dumps({"message": "模拟模式响应"}, ensure_ascii=False)
