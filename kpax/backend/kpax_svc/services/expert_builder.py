"""Expert builder: generates a lineup of domain experts for any decision.

Unlike Agent X Lab's academic-only agents, KPAX experts can be economists,
lawyers, psychologists, industry analysts — whatever the question demands.
"""

from __future__ import annotations

import json
import logging

from kpax_svc.clients.llm_client import chat_completion

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是 KPAX 的专家阵容规划师。根据用户的问题和背景信息，你需要设计一组 3-5 位专家来进行多角度辩论分析。

专家不限于学术学者，可以是：
- 经济学家、金融分析师
- 律师、法律顾问
- 心理学家、职业规划师
- 行业分析师、创业顾问
- 数据科学家、统计学家
- 医学专家、营养学家
- 体育分析师、博弈论专家
- 或者任何和问题最相关的专业角色

每个专家需要：
- name: 专家的称呼（如 "资深房地产分析师"、"行为经济学家"）
- role: 他在这次分析中的角色定位（一句话，如 "从市场数据角度评估投资风险"）
- perspective: 他会从什么独特角度分析问题（2-3 句话）
- stance_hint: 他可能倾向的立场（"cautious" / "optimistic" / "neutral" / "contrarian"），确保阵容中有不同立场

原则：
- 专家之间必须有观点张力，不能全是同一个方向
- 至少一位专家扮演质疑者角色
- 每位专家的分析角度必须和用户的具体问题直接相关
- 阵容要覆盖问题的核心维度（风险、收益、情感、实操等）

回复必须是严格 JSON：
{
  "experts": [
    {
      "name": "...",
      "role": "...",
      "perspective": "...",
      "stance_hint": "..."
    }
  ],
  "analysis_angles": ["角度1", "角度2", "..."],
  "core_tension": "这个问题最核心的矛盾点是什么（一句话）"
}
"""


async def build_experts(question: str, context_summary: str) -> dict:
    """Generate expert lineup based on the question and collected context."""
    user_msg = f"用户问题：{question}\n\n背景信息：\n{context_summary}"

    raw = await chat_completion(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.4,
        max_tokens=2000,
    )

    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        parsed = json.loads(raw[start:end])
    except (ValueError, json.JSONDecodeError) as exc:
        logger.error("Failed to parse expert_builder LLM output: %s\n%s", exc, raw)
        return _fallback(question)

    if "experts" not in parsed:
        return _fallback(question)

    return parsed


def experts_to_system_prompts(
    experts: list[dict], question: str, context_summary: str
) -> list[dict]:
    """Convert expert definitions into debate-engine-compatible agent specs.

    Returns a list of dicts that match the shape expected for DebateAgent creation.
    """
    specs = []
    for i, expert in enumerate(experts):
        name = expert["name"]
        role = expert.get("role", "")
        perspective = expert.get("perspective", "")
        stance = expert.get("stance_hint", "neutral")

        system_prompt = (
            f"你是一位{name}。\n\n"
            f"你在这次分析中的角色：{role}\n\n"
            f"你的分析视角：{perspective}\n\n"
            f"## 用户的核心问题\n{question}\n\n"
            f"## 用户提供的背景信息\n{context_summary}\n\n"
            f"要求：\n"
            f"- 从你的专业角度出发，给出具体、有依据的分析\n"
            f"- 不要泛泛而谈，要结合用户的具体情况\n"
            f"- 如果你认为其他专家的观点有问题，直接反驳\n"
            f"- 每次发言结尾给出你的具体建议或判断\n"
            f"- 用中文回复，简洁有力"
        )

        specs.append({
            "agent_name": name,
            "persona": stance,
            "rank": "professor",
            "weight": 50,
            "stance": stance,
            "system_prompt": system_prompt,
            "sort_order": i,
        })

    moderator_prompt = (
        "你是这次多角度分析的主持人。\n\n"
        f"用户的核心问题：{question}\n\n"
        f"用户的背景：{context_summary}\n\n"
        "你的任务：\n"
        "- 综合各位专家的观点，找出共识和分歧\n"
        "- 确保讨论始终围绕用户的实际问题\n"
        "- 在每轮结束时指出哪些角度已经分析到位，哪些还需要深入\n"
        "- 保持中立，不偏向任何一方\n"
        "- 用中文回复"
    )
    specs.append({
        "agent_name": "主持人",
        "persona": "moderator",
        "rank": "professor",
        "weight": 50,
        "stance": None,
        "system_prompt": moderator_prompt,
        "sort_order": len(experts),
    })

    return specs


def _fallback(question: str) -> dict:
    return {
        "experts": [
            {
                "name": "风险评估分析师",
                "role": "识别潜在风险和不确定性",
                "perspective": "从风险管理角度出发，评估各种可能出错的地方，量化不确定性。",
                "stance_hint": "cautious",
            },
            {
                "name": "机会发掘顾问",
                "role": "发现潜在收益和机会",
                "perspective": "关注正面可能性，寻找别人没看到的机会点。",
                "stance_hint": "optimistic",
            },
            {
                "name": "实操落地专家",
                "role": "评估可行性和执行难度",
                "perspective": "关注具体怎么做、需要什么资源、时间表是否现实。",
                "stance_hint": "neutral",
            },
        ],
        "analysis_angles": ["风险评估", "机会分析", "可行性验证"],
        "core_tension": "收益预期与风险承受之间的平衡",
    }
