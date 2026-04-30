"""Report generator: debate results → structured one-page analysis report."""

from __future__ import annotations

import json
import logging

from kpax_svc.clients.llm_client import chat_completion

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是 KPAX 的报告生成器。你会收到一场多专家辩论分析的完整记录，需要生成一份结构化的分析报告。

报告必须包含以下部分：

1. executive_summary: 一段话总结结论（不超过 150 字）
2. question_reframe: 用更精确的方式重新定义用户的问题（帮用户看到他可能没意识到的问题维度）
3. pro_arguments: 支持行动的论点列表，每个包含 {point, evidence, expert}
4. con_arguments: 反对/需谨慎的论点列表，每个包含 {point, evidence, expert}
5. key_disagreements: 专家之间的核心分歧点列表，每个包含 {topic, positions}（positions 是不同专家的立场）
6. blind_spots: 分析中可能遗漏的角度或信息
7. action_items: 具体可执行的建议列表，按优先级排序，每个包含 {action, rationale, urgency}（urgency: high/medium/low）
8. follow_up_questions: 建议用户进一步思考的问题（3-5 个）

原则：
- 结论要诚实，不回避不确定性
- 引用专家观点时标注是谁说的
- action_items 要具体到可以直接执行
- 不要套话和废话

回复必须是严格 JSON。
"""


async def generate_report(
    question: str,
    context_summary: str,
    debate_messages: list[dict],
    debate_summary: dict[str, str] | None = None,
) -> dict:
    """Generate a structured report from debate results."""
    msg_text = _format_messages(debate_messages)

    summary_block = ""
    if debate_summary:
        parts = []
        for k, v in debate_summary.items():
            parts.append(f"### {k}\n{v}")
        summary_block = "\n\n".join(parts)

    user_msg = (
        f"## 用户原始问题\n{question}\n\n"
        f"## 背景信息\n{context_summary}\n\n"
        f"## 辩论记录\n{msg_text}\n\n"
    )
    if summary_block:
        user_msg += f"## 主持人总结\n{summary_block}\n\n"

    user_msg += "请根据以上内容生成结构化分析报告。"

    raw = await chat_completion(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.3,
        max_tokens=4000,
    )

    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        parsed = json.loads(raw[start:end])
    except (ValueError, json.JSONDecodeError) as exc:
        logger.error("Failed to parse report_generator output: %s\n%s", exc, raw)
        return _fallback_report(question, raw)

    return parsed


async def generate_followup(
    report: dict, followup_question: str, debate_messages: list[dict]
) -> dict:
    """Generate a follow-up analysis on a specific angle of the report."""
    msg_text = _format_messages(debate_messages)

    user_msg = (
        f"## 之前的分析报告\n{json.dumps(report, ensure_ascii=False, indent=2)}\n\n"
        f"## 辩论记录\n{msg_text}\n\n"
        f"## 用户追问\n{followup_question}\n\n"
        "请针对用户的追问，基于之前的辩论内容做深入分析。回复 JSON 格式：\n"
        '{"answer": "详细回答", "additional_insights": ["补充洞察1", ...], '
        '"revised_action_items": [{"action": "...", "rationale": "...", "urgency": "..."}]}'
    )

    raw = await chat_completion(
        messages=[
            {"role": "system", "content": "你是 KPAX 的分析师，擅长深入解答用户的追问。"},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.3,
        max_tokens=2000,
    )

    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        return json.loads(raw[start:end])
    except (ValueError, json.JSONDecodeError):
        return {"answer": raw, "additional_insights": [], "revised_action_items": []}


def _format_messages(messages: list[dict]) -> str:
    lines = []
    for m in messages:
        speaker = m.get("agent_name", m.get("role", "unknown"))
        content = m.get("content", "")
        rnd = m.get("round_number", "?")
        lines.append(f"[Round {rnd}] {speaker}:\n{content}\n")
    return "\n".join(lines)


def _fallback_report(question: str, raw_text: str) -> dict:
    return {
        "executive_summary": "报告生成过程中遇到格式问题，以下是原始分析内容。",
        "question_reframe": question,
        "pro_arguments": [],
        "con_arguments": [],
        "key_disagreements": [],
        "blind_spots": ["报告格式解析失败，建议重新生成"],
        "action_items": [],
        "follow_up_questions": [],
        "_raw": raw_text,
    }
