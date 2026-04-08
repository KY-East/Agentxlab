"""Multi-model AI abstraction layer using LiteLLM."""

from __future__ import annotations

import os

import litellm

from app.config import settings

if settings.deepseek_api_key and "DEEPSEEK_API_KEY" not in os.environ:
    os.environ["DEEPSEEK_API_KEY"] = settings.deepseek_api_key

SYSTEM_PROMPTS = {
    "en": (
        "You are a research hypothesis generator for Agent X Lab, an interdisciplinary research lab.\n\n"
        "Given academic disciplines with NO existing research at their intersection, "
        "generate a rigorous, novel research hypothesis. Structure your output as:\n\n"
        "## Research Hypothesis\nOne clear sentence.\n\n"
        "## Conceptual Tension\nWhat unexplored connection exists? (bullet points)\n\n"
        "## Theoretical Anchors\nKey scholars/theories from each discipline. (bullet points)\n\n"
        "## Testable Research Question\nOne concrete question.\n\n"
        "## Theoretical Significance\nWhy this matters. (bullet points)\n\n"
        "Respond ONLY in English. Use bullet points, be concise."
    ),
    "zh": (
        "你是 Agent X Lab 的研究假设生成器，一个跨学科研究实验室。\n\n"
        "给定一组目前在交叉领域没有已知研究的学科，生成一个严谨、新颖的研究假设。按以下结构输出：\n\n"
        "## 研究假设\n一句话清晰陈述。\n\n"
        "## 概念张力\n学科之间存在什么未被探索的联系？（要点列表）\n\n"
        "## 理论锚点\n每个学科的关键学者/理论。（要点列表）\n\n"
        "## 可检验的研究问题\n一个具体的问题。\n\n"
        "## 理论意义\n为什么这个交叉领域重要。（要点列表）\n\n"
        "只用中文回复。使用要点列表，精练简洁。"
    ),
}


def build_prompt(discipline_names: list[str], language: str = "zh") -> str:
    joined = " x ".join(discipline_names)
    if language == "zh":
        return (
            f"为以下学科交叉生成研究假设：{joined}\n\n"
            f"这 {len(discipline_names)} 个学科目前在我们的知识库中没有已记录的交叉研究。"
            f"请提出可以研究的方向及其重要性。"
        )
    return (
        f"Generate a research hypothesis for the intersection of: {joined}\n\n"
        f"These {len(discipline_names)} disciplines currently have no documented "
        f"research at their intersection in our knowledge base. Propose what could "
        f"be studied here and why it matters."
    )


async def chat_completion(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    retries: int = 2,
) -> str:
    """Generic LLM call with retry for transient API errors."""
    import asyncio
    import logging

    logger = logging.getLogger(__name__)
    model = model or settings.default_ai_model

    for attempt in range(1, retries + 2):
        try:
            response = await litellm.acompletion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as exc:
            if attempt > retries:
                raise
            logger.warning("LLM call attempt %d failed (%s), retrying...", attempt, exc)
            await asyncio.sleep(2 * attempt)


async def generate_hypothesis(
    discipline_names: list[str],
    model: str | None = None,
    language: str = "zh",
) -> str:
    lang = language if language in ("zh", "en") else "zh"
    system = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["en"])
    user_prompt = build_prompt(discipline_names, lang)
    return await chat_completion(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt},
        ],
        model=model,
    )


EXPLORE_SYSTEM_PROMPTS = {
    "en": (
        "You are an interdisciplinary research advisor at Agent X Lab.\n\n"
        "The user is exploring a research intersection between academic disciplines. "
        "Your role is to suggest promising research angles, refine ideas through conversation, "
        "and ultimately help the user arrive at a well-formed research hypothesis.\n\n"
        "Conversation flow:\n"
        "1. First, analyze the intersection context and suggest 2-3 distinct research angles.\n"
        "2. Let the user pick or propose their own direction, then discuss it.\n"
        "3. When the user is satisfied, produce the final hypothesis.\n\n"
        "Respond ONLY with valid JSON:\n"
        '{"reply": "<your conversational reply in markdown>", '
        '"hypothesis": "<full hypothesis text if finalized, else null>", '
        '"suggestions": ["<angle 1>", "<angle 2>", ...] }\n\n'
        "All output in English."
    ),
    "zh": (
        "你是 Agent X Lab 的跨学科研究顾问。\n\n"
        "用户正在探索学科交叉的研究方向。你的职责是建议有前景的研究角度，"
        "通过对话完善想法，最终帮助用户形成一个完整的研究假设。\n\n"
        "对话流程：\n"
        "1. 首先，分析交叉领域的背景，建议 2-3 个不同的研究角度。\n"
        "2. 让用户选择或提出自己的方向，然后讨论细化。\n"
        "3. 当用户满意后，产出最终的假设。\n\n"
        "只用有效 JSON 回复：\n"
        '{"reply": "<你的对话回复，用 markdown>", '
        '"hypothesis": "<如果已确定，输出完整假设文本，否则为 null>", '
        '"suggestions": ["<角度 1>", "<角度 2>", ...] }\n\n'
        "所有内容用中文输出。"
    ),
}


async def chat_hypothesis(
    discipline_names: list[str],
    context_text: str,
    user_message: str,
    history: list[dict],
    language: str = "zh",
) -> dict:
    """Conversational hypothesis exploration."""
    import json

    lang = language if language in ("zh", "en") else "zh"
    system = EXPLORE_SYSTEM_PROMPTS.get(lang, EXPLORE_SYSTEM_PROMPTS["en"])

    joined = " x ".join(discipline_names)
    if lang == "zh":
        context_block = f"交叉学科：{joined}\n背景信息：{context_text}"
    else:
        context_block = f"Disciplines: {joined}\nContext: {context_text}"

    messages: list[dict] = [{"role": "system", "content": system}]

    if history:
        messages.extend(history)
        if user_message:
            messages.append({"role": "user", "content": user_message})
    elif user_message:
        messages.append({"role": "user", "content": f"{context_block}\n\n{user_message}"})
    else:
        if lang == "zh":
            messages.append({"role": "user", "content": f"{context_block}\n\n请分析这个交叉领域，给出 2-3 个可探索的研究角度。"})
        else:
            messages.append({"role": "user", "content": f"{context_block}\n\nPlease analyze this intersection and suggest 2-3 research angles."})

    import logging as _log
    _log.getLogger(__name__).info("chat_hypothesis messages: %s", [{"role": m["role"], "content": m["content"][:200]} for m in messages])
    raw = await chat_completion(messages=messages, temperature=0.6, max_tokens=2000)

    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            parsed = json.loads(raw[start:end])
        else:
            parsed = {"reply": raw, "hypothesis": None, "suggestions": []}
    except json.JSONDecodeError:
        parsed = {"reply": raw, "hypothesis": None, "suggestions": []}

    return {
        "reply": parsed.get("reply", raw),
        "hypothesis": parsed.get("hypothesis"),
        "suggestions": parsed.get("suggestions", []),
    }
