"""Extract cross-domain sparks from agent debate messages.

A "spark" is a cross-disciplinary analogy, concept transfer, fusion, or
inversion that may not have been obvious before. This service uses a lightweight
LLM call to identify and score such sparks in real time during debates.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy.orm import Session

from app.models.debate import DebateAgent, DebateMessage
from app.models.spark import Spark
from app.services.ai_provider import chat_completion

logger = logging.getLogger(__name__)

EXTRACTION_PROMPTS = {
    "en": """\
You are a research novelty detector. Given a message from an interdisciplinary \
academic debate, identify any **cross-domain sparks** — ideas that connect two \
different disciplines in a surprising or creative way.

A spark must involve at least two distinct disciplines. It can be:
- **analogy**: drawing a parallel between concepts from different fields
- **transfer**: applying a method/theory from one field to another
- **fusion**: combining ideas from multiple fields into something new
- **inversion**: flipping a concept from one field to challenge another

For each spark found, provide:
- "content": a one-sentence description of the spark
- "novelty_type": one of "analogy", "transfer", "fusion", "inversion"
- "novelty_score": 0.0 to 1.0 (how surprising/novel this connection is; \
0.3 = somewhat expected, 0.7 = genuinely surprising, 0.9+ = breakthrough-level)
- "reasoning": brief explanation of why this is novel (1-2 sentences)
- "source_discipline": the discipline the idea originates from
- "target_discipline": the discipline the idea is applied to

If the message contains NO cross-domain sparks, return an empty array.
All output must be in English.

Respond ONLY with a JSON array. Example:
[
  {
    "content": "Using social network information propagation models for neural network pruning",
    "novelty_type": "transfer",
    "novelty_score": 0.75,
    "reasoning": "Network pruning typically uses magnitude-based methods; social contagion models offer a structurally different approach.",
    "source_discipline": "Sociology",
    "target_discipline": "Computer Science"
  }
]
""",
    "zh": """\
你是一个研究新颖性检测器。给定一条来自跨学科学术辩论的消息，识别其中的**跨领域火花**——\
以令人惊讶或创造性的方式连接两个不同学科的想法。

火花必须涉及至少两个不同的学科。类型包括：
- **analogy**（类比）：在不同领域的概念之间建立平行关系
- **transfer**（迁移）：将一个领域的方法/理论应用到另一个领域
- **fusion**（融合）：将多个领域的想法组合成新事物
- **inversion**（反转）：翻转一个领域的概念来挑战另一个领域

对于发现的每个火花，提供：
- "content": 一句话描述该火花（中文）
- "novelty_type": "analogy"、"transfer"、"fusion"、"inversion" 之一
- "novelty_score": 0.0 到 1.0（该连接的惊人/新颖程度；\
0.3 = 比较常见, 0.7 = 真正令人惊讶, 0.9+ = 突破性）
- "reasoning": 简要解释为什么这是新颖的（1-2句，中文）
- "source_discipline": 想法起源的学科（英文名）
- "target_discipline": 想法应用到的学科（英文名）

如果消息中没有跨领域火花，返回空数组。
所有 content 和 reasoning 字段必须使用中文。

仅以 JSON 数组格式回复。
""",
}


def _build_extraction_messages(
    agent_name: str,
    agent_discipline: str | None,
    message_content: str,
    debate_disciplines: list[str],
    language: str = "en",
) -> list[dict[str, str]]:
    context = f"Debate disciplines: {', '.join(debate_disciplines)}"
    if agent_discipline:
        context += f"\nSpeaker discipline: {agent_discipline}"
    context += f"\nSpeaker: {agent_name}"

    prompt = EXTRACTION_PROMPTS.get(language, EXTRACTION_PROMPTS["en"])
    return [
        {"role": "system", "content": prompt},
        {
            "role": "user",
            "content": f"{context}\n\n---\nMessage:\n{message_content}",
        },
    ]


def _parse_sparks_response(raw: str) -> list[dict[str, Any]]:
    """Best-effort parse of LLM JSON array response."""
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        raw = "\n".join(lines)

    start = raw.find("[")
    end = raw.rfind("]")
    if start == -1 or end == -1:
        return []

    try:
        parsed = json.loads(raw[start : end + 1])
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass
    return []


async def extract_sparks_from_message(
    message: DebateMessage,
    agent: DebateAgent,
    debate_discipline_names: list[str],
    discipline_name_to_id: dict[str, int],
    db: Session,
    language: str = "en",
) -> list[Spark]:
    """Analyze a single agent message and persist any sparks found.

    Returns the list of newly created Spark objects (already added to session).
    """
    agent_disc_name = agent.discipline.name_en if agent.discipline else None

    messages = _build_extraction_messages(
        agent_name=agent.agent_name,
        agent_discipline=agent_disc_name,
        message_content=message.content,
        debate_disciplines=debate_discipline_names,
        language=language,
    )

    try:
        raw = await chat_completion(messages, temperature=0.2, max_tokens=1000)
    except Exception as exc:
        logger.warning("Spark extraction LLM call failed for message %d: %s", message.id, exc)
        return []

    parsed = _parse_sparks_response(raw)
    if not parsed:
        return []

    created: list[Spark] = []
    for item in parsed:
        content = item.get("content", "").strip()
        if not content:
            continue

        ntype = item.get("novelty_type", "analogy")
        if ntype not in ("analogy", "transfer", "fusion", "inversion"):
            ntype = "analogy"

        score = item.get("novelty_score", 0.0)
        try:
            score = max(0.0, min(1.0, float(score)))
        except (ValueError, TypeError):
            score = 0.0

        src_name = item.get("source_discipline", "")
        tgt_name = item.get("target_discipline", "")
        src_id = _fuzzy_match_discipline(src_name, discipline_name_to_id)
        tgt_id = _fuzzy_match_discipline(tgt_name, discipline_name_to_id)

        spark = Spark(
            debate_id=message.debate_id,
            message_id=message.id,
            agent_id=agent.id,
            source_discipline_id=src_id,
            target_discipline_id=tgt_id,
            content=content,
            novelty_type=ntype,
            novelty_score=score,
            reasoning=item.get("reasoning"),
            verification_status="unverified",
        )
        db.add(spark)
        created.append(spark)

    logger.info(
        "Extracted %d spark(s) from message %d (agent %s)",
        len(created), message.id, agent.agent_name,
    )
    return created


def _fuzzy_match_discipline(name: str, name_to_id: dict[str, int]) -> int | None:
    """Try exact match first, then case-insensitive substring match."""
    if not name:
        return None
    if name in name_to_id:
        return name_to_id[name]
    lower = name.lower()
    for k, v in name_to_id.items():
        if k.lower() == lower:
            return v
    for k, v in name_to_id.items():
        if lower in k.lower() or k.lower() in lower:
            return v
    return None
