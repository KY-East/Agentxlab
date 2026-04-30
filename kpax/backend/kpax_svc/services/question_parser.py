"""Question parser: one sentence → structured context questions.

Takes a user's question and uses LLM to generate the most relevant
background questions with appropriate interaction types (select, slider,
tags, text) tailored to that specific decision.
"""

from __future__ import annotations

import json
import logging

from kpax_svc.clients.llm_client import chat_completion

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是 KPAX 的问题解析器。用户会输入一个需要做决策的问题。

你的任务是：
1. 判断问题类型（如：投资决策、职业选择、购房决策、体育赛事分析、教育规划、健康决策等）
2. 生成 3-7 个最关键的背景问题，帮助后续的专家分析更加精准

每个背景问题必须包含：
- field_id: 英文标识符（snake_case）
- label: 中文问题文本
- description: 为什么需要这个信息（一句话）
- input_type: 交互类型，只能是以下之一：
  - "select": 单选（必须提供 options 数组）
  - "multi_select": 多选（必须提供 options 数组）
  - "slider": 数值滑块（必须提供 slider_config: {min, max, step, unit}）
  - "tags": 标签选择（必须提供 options 数组，可多选）
  - "text": 自由文本输入
- options: 选项数组（select/multi_select/tags 类型必填），每个选项 {value, label}
- slider_config: 滑块配置（slider 类型必填），{min, max, step, unit}
- required: 是否必填（布尔值）

原则：
- 能用点选、滑块、标签解决的不要让用户打字
- 只有真正需要用户自己描述的才用 text 类型
- 问题要和这个具体决策直接相关，不问废话
- 按重要程度排序，最关键的排最前面

回复必须是严格 JSON，格式：
{
  "question_type": "问题类型",
  "question_summary": "用一句话重述用户的核心决策",
  "context_fields": [ ... ]
}
"""


async def parse_question(question: str) -> dict:
    """Analyze a user question and generate tailored context-gathering fields."""
    raw = await chat_completion(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        temperature=0.3,
        max_tokens=3000,
    )

    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        parsed = json.loads(raw[start:end])
    except (ValueError, json.JSONDecodeError) as exc:
        logger.error("Failed to parse question_parser LLM output: %s\n%s", exc, raw)
        return _fallback(question)

    if "context_fields" not in parsed:
        return _fallback(question)

    return parsed


def _fallback(question: str) -> dict:
    """Minimal fallback if LLM output is unusable."""
    return {
        "question_type": "general",
        "question_summary": question,
        "context_fields": [
            {
                "field_id": "background",
                "label": "请描述一下你的具体情况和背景",
                "description": "帮助专家更好地理解你的处境",
                "input_type": "text",
                "required": True,
            },
            {
                "field_id": "concern",
                "label": "你最大的顾虑是什么？",
                "description": "让分析聚焦在你最关心的风险上",
                "input_type": "text",
                "required": False,
            },
            {
                "field_id": "timeline",
                "label": "这个决定需要在多长时间内做出？",
                "description": "时间压力会影响分析建议",
                "input_type": "select",
                "options": [
                    {"value": "urgent", "label": "非常紧急（几天内）"},
                    {"value": "weeks", "label": "几周内"},
                    {"value": "months", "label": "几个月"},
                    {"value": "no_rush", "label": "不着急"},
                ],
                "required": False,
            },
        ],
    }
