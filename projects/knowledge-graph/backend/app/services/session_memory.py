"""Session-level memory compression for debates.

Implements the hybrid context strategy from the Memory System Architecture:
- Round 1-2: full history (no compression)
- Round 3+: compressed summary of Round 1~N-1 + full Round N messages + unresolved questions

The compression threshold adapts to debate depth:
- quick:    compress from Round 2
- standard: compress from Round 3
- deep:     compress from Round 3
- max:      compress from Round 4

On compression failure, falls back to full history (no crash).
"""

from __future__ import annotations

import logging
from typing import Any

from app.models.debate import DebateMessage
from app.services.ai_provider import chat_completion

logger = logging.getLogger(__name__)

COMPRESSION_THRESHOLD = {
    "quick": 2,
    "standard": 3,
    "deep": 3,
    "max": 4,
}

COMPRESS_PROMPT_ZH = """\
你是一个学术辩论的上下文压缩器。你的任务是把多轮辩论历史压缩成一份简洁的摘要。

## 输入
你会收到辩论历史（多个 agent 的发言）。

## 输出要求
严格按以下格式输出，不要加任何前缀或解释：

## 已达成的共识
- [列出所有学科已经认同的核心观点]

## 关键分歧
- [列出仍在争论的核心问题，标注哪个学科持什么立场]

## 未解决的质疑
- [列出已被提出但尚未被回应的具体质疑，标注"学科A质疑了X，但学科B未回应"]

## 各学科核心论点
- [学科名]: [该学科最强的 1-2 个论点的一句话总结]

规则：
- 只用中文
- 每个要点一句话，不展开
- 未解决的质疑是最重要的部分——下一轮 agent 需要看到它来回应
- 总长度控制在 300-500 字"""

COMPRESS_PROMPT_EN = """\
You are a context compressor for an academic debate. Compress multi-round debate history into a concise summary.

## Output format (strict, no preamble):

## Consensus Reached
- [List agreed-upon points across disciplines]

## Key Disagreements
- [List contested points, noting which discipline holds which position]

## Unresolved Challenges
- [List specific challenges raised but not yet addressed: "Discipline A challenged X, but Discipline B did not respond"]

## Core Arguments by Discipline
- [Discipline]: [1-2 sentence summary of their strongest argument]

Rules:
- English only
- One sentence per bullet point
- Unresolved challenges are the most critical section
- Total length: 200-400 words"""


def _should_compress(current_round: int, depth: str) -> bool:
    threshold = COMPRESSION_THRESHOLD.get(depth, 3)
    return current_round >= threshold


def _split_messages_by_round(
    messages: list[DebateMessage],
) -> dict[int, list[DebateMessage]]:
    """Group messages by round_number."""
    by_round: dict[int, list[DebateMessage]] = {}
    for m in messages:
        rn = m.round_number or 1
        by_round.setdefault(rn, []).append(m)
    return by_round


def _format_messages_for_compression(messages: list[DebateMessage]) -> str:
    """Format debate messages into plain text for the compression LLM."""
    lines = []
    for m in messages:
        label = m.agent.agent_name if m.agent else "System"
        lines.append(f"[{label}]: {m.content}")
    return "\n\n".join(lines)


def _format_messages_as_history(messages: list[DebateMessage]) -> list[dict[str, str]]:
    """Convert messages to LLM chat format (same as _build_history in debate_engine)."""
    result = []
    for m in messages:
        if m.role == "agent" and m.agent:
            result.append({"role": "user", "content": f"[{m.agent.agent_name}]: {m.content}"})
        elif m.role == "system":
            result.append({"role": "system", "content": m.content})
        elif m.role == "user":
            result.append({"role": "user", "content": m.content})
    return result


async def compress_history(
    messages: list[DebateMessage],
    current_round: int,
    *,
    language: str = "zh",
    user_id: int | None = None,
    db: Any = None,
) -> str | None:
    """Compress rounds 1~(N-1) into a structured summary.

    Returns the compressed summary string, or None on failure.
    """
    by_round = _split_messages_by_round(messages)

    rounds_to_compress = sorted(r for r in by_round if r < current_round)
    if not rounds_to_compress:
        return None

    msgs_to_compress = []
    for r in rounds_to_compress:
        msgs_to_compress.extend(by_round[r])

    if not msgs_to_compress:
        return None

    text = _format_messages_for_compression(msgs_to_compress)
    sys_prompt = COMPRESS_PROMPT_ZH if language == "zh" else COMPRESS_PROMPT_EN

    try:
        summary = await chat_completion(
            [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": text},
            ],
            temperature=0.2,
            max_tokens=800,
            user_id=user_id,
            db=db,
        )
        logger.info(
            "Compressed rounds %s (%d messages, ~%d chars) -> %d chars",
            rounds_to_compress, len(msgs_to_compress), len(text), len(summary),
        )
        return summary
    except Exception as exc:
        logger.warning("Session compression failed, will fall back to full history: %s", exc)
        return None


async def build_compressed_context(
    all_messages: list[DebateMessage],
    current_round: int,
    *,
    depth: str = "standard",
    language: str = "zh",
    user_id: int | None = None,
    db: Any = None,
) -> list[dict[str, str]]:
    """Build the hybrid context for a new round.

    Returns a list of chat messages ready for LLM injection:
    - If compression triggers: [compressed summary] + [last round raw messages]
    - If no compression needed or compression fails: full history (fallback)
    """
    if not _should_compress(current_round, depth):
        return _format_messages_as_history(all_messages)

    by_round = _split_messages_by_round(all_messages)
    last_round = current_round - 1

    summary = await compress_history(
        all_messages, current_round,
        language=language, user_id=user_id, db=db,
    )

    if summary is None:
        logger.info("Compression returned None, falling back to full history")
        return _format_messages_as_history(all_messages)

    result: list[dict[str, str]] = []

    result.append({
        "role": "system",
        "content": (
            "以下是前几轮辩论的压缩摘要。请特别注意【未解决的质疑】部分——"
            "如果有针对你的学科的质疑，你必须在本轮回应。"
            if language == "zh" else
            "Below is a compressed summary of previous debate rounds. "
            "Pay special attention to 'Unresolved Challenges' — "
            "if any challenge targets your discipline, you MUST respond this round."
        ),
    })
    result.append({"role": "user", "content": summary})

    last_round_msgs = by_round.get(last_round, [])
    if last_round_msgs:
        result.extend(_format_messages_as_history(last_round_msgs))

    return result
