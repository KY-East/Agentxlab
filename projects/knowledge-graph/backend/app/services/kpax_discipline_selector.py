"""KPAX v0 discipline selector.

Given a user question + user_context, return 3-7 disciplines to involve in the
debate. This is the minimum-viable dynamic selection mandated by
``kpax_api_spec.md §13.3 §7.3`` (v1.3).

v0 candidate pool is the experiment 7 disciplines (Physics / Mathematics /
Economics / Psychology / Sociology / Computer Science / Art & Humanities).
v0.1 will widen the pool to the full ``disciplines`` table.

The selector makes ONE cheap LLM call per question. The model picks:
  - which N disciplines (odd, 3 / 5 / 7) from the pool are most relevant
  - why each is relevant (reason strings kept in logs, not returned)

KPAX 产品约定（Ken 2026-04-17 晚纠正）:
  每场出席化身 3 / 5 / 7 位（奇数便于决断，最少 3）。和 AXL 实验里的
  "2-7 学科" 口径不同 — AXL 研究维度允许 2 起步，KPAX 产品决策不允许
  "只有 2 位化身 + 一个主持人" 的薄组合。

No caching in v0（PRD §5: explicit "no endpoint-level cache"）。
"""

from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy.orm import Session

from app.models.discipline import Discipline
from app.services.ai_provider import chat_completion

logger = logging.getLogger(__name__)

# v0 候选池: 实验 7 学科 baseline（PRD §13.3 §7.3）
# name_en 用于 DB 查询（OpenAlex 标准名），name_zh 用于用户侧展示
V0_CANDIDATE_POOL_EN: tuple[str, ...] = (
    "Physics",
    "Mathematics",
    "Economics",
    "Psychology",
    "Sociology",
    "Computer science",
    "Art",
)

# KPAX 产品约定: 奇数 + 最少 3
ALLOWED_AGENT_COUNTS: tuple[int, ...] = (3, 5, 7)


class DisciplineSelectionError(Exception):
    """Raised when the LLM output cannot be parsed into a valid selection."""


def _load_candidate_disciplines(db: Session) -> list[Discipline]:
    """Load v0 candidate pool disciplines from DB by name_en.

    Order follows V0_CANDIDATE_POOL_EN exactly so prompt and return order
    are deterministic. Missing names fall back to the first N from the
    disciplines table (warn-logged) so v0 does not hard-fail on seed gaps.
    """
    by_name = {
        d.name_en: d
        for d in db.query(Discipline).filter(
            Discipline.name_en.in_(V0_CANDIDATE_POOL_EN)
        ).all()
    }
    ordered: list[Discipline] = []
    missing: list[str] = []
    for name in V0_CANDIDATE_POOL_EN:
        if name in by_name:
            ordered.append(by_name[name])
        else:
            missing.append(name)

    if missing:
        logger.warning(
            "kpax_discipline_selector: candidate pool missing %d disciplines in DB: %s",
            len(missing), missing,
        )

    if len(ordered) < 3:
        fallback = (
            db.query(Discipline)
            .filter(Discipline.parent_id.is_(None))
            .order_by(Discipline.id)
            .limit(7)
            .all()
        )
        logger.warning(
            "kpax_discipline_selector: only %d candidates resolved, falling back to top-%d root disciplines",
            len(ordered), len(fallback),
        )
        ordered = fallback

    return ordered


def _build_selector_prompt(
    question: str,
    user_context: dict[str, Any],
    candidates: list[Discipline],
) -> str:
    lines = [
        "你是 KPAX 化身团召唤调度员。用户提出了一个真实决策问题。",
        "从下面的化身候选池里，选 3 / 5 / 7 位（必须奇数，便于辩论形成判断）。",
        "",
        "原则：",
        "- 只选和问题真正相关的化身，不要为了凑数硬塞",
        "- 不同化身之间视角要有差异（避免全部经济视角 / 全部心理视角）",
        "- 人数按问题复杂度定：简单题 3 位，中等 5 位，跨面广的复杂决策 7 位",
        "",
        "候选池（v0）：",
    ]
    for idx, d in enumerate(candidates, 1):
        zh = d.name_zh or d.name_en
        lines.append(f"  {idx}. {d.name_en} / {zh} (id={d.id})")
    lines += [
        "",
        f"用户问题: {question}",
    ]
    if user_context:
        lines.append(f"用户上下文: {json.dumps(user_context, ensure_ascii=False)}")

    lines += [
        "",
        "只用 JSON 回复，不要任何其他文字：",
        '{"agent_count": 3, "selected_ids": [<discipline_id>, ...], '
        '"rationale": "<一句话说明为什么挑这几个>"}',
        "",
        "约束：agent_count ∈ {3, 5, 7}，selected_ids 长度 == agent_count，"
        "所有 id 必须来自上面候选池。",
    ]
    return "\n".join(lines)


def _extract_json(raw: str) -> dict[str, Any]:
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        return json.loads(raw[start:end])
    except (ValueError, json.JSONDecodeError) as exc:
        raise DisciplineSelectionError(f"LLM output not JSON: {raw[:200]}") from exc


def _fallback_selection(candidates: list[Discipline]) -> tuple[list[Discipline], int]:
    """When LLM output is unusable, pick first 3 from candidate pool.

    Chosen over raising because v0 UX priority is "always produce a debate";
    a slightly suboptimal selection beats a hard 500 for the user.
    """
    picked = candidates[:3]
    logger.warning(
        "kpax_discipline_selector: falling back to first %d candidates: %s",
        len(picked), [d.name_en for d in picked],
    )
    return picked, 3


async def select_disciplines(
    question: str,
    user_context: dict[str, Any],
    db: Session,
    *,
    user_id: int | None = None,
) -> tuple[list[Discipline], int]:
    """Pick 3 / 5 / 7 disciplines for the KPAX debate.

    Returns (disciplines, agent_count).
    agent_count is the moderator-excluded headcount KPAX UI needs to seat.

    Spec: kpax_api_spec.md §13.3 §7.3.
    """
    candidates = _load_candidate_disciplines(db)
    if not candidates:
        raise DisciplineSelectionError(
            "kpax_discipline_selector: no candidate disciplines available in DB"
        )

    prompt = _build_selector_prompt(question, user_context, candidates)
    try:
        raw = await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=400,
            user_id=user_id,
            db=db,
        )
    except Exception as exc:
        logger.warning("kpax_discipline_selector: LLM call failed (%s), falling back", exc)
        return _fallback_selection(candidates)

    try:
        parsed = _extract_json(raw)
    except DisciplineSelectionError as exc:
        logger.warning("kpax_discipline_selector: parse failed (%s), falling back", exc)
        return _fallback_selection(candidates)

    agent_count = parsed.get("agent_count")
    selected_ids = parsed.get("selected_ids") or []

    if agent_count not in ALLOWED_AGENT_COUNTS:
        logger.warning(
            "kpax_discipline_selector: invalid agent_count=%r, falling back", agent_count
        )
        return _fallback_selection(candidates)

    if not isinstance(selected_ids, list) or len(selected_ids) != agent_count:
        logger.warning(
            "kpax_discipline_selector: selected_ids length mismatch (%d vs %d), falling back",
            len(selected_ids) if isinstance(selected_ids, list) else -1, agent_count,
        )
        return _fallback_selection(candidates)

    by_id = {d.id: d for d in candidates}
    picked: list[Discipline] = []
    for did in selected_ids:
        if did in by_id and by_id[did] not in picked:
            picked.append(by_id[did])
    if len(picked) != agent_count:
        logger.warning(
            "kpax_discipline_selector: some ids not in candidate pool (got %d/%d), falling back",
            len(picked), agent_count,
        )
        return _fallback_selection(candidates)

    rationale = parsed.get("rationale", "")
    logger.info(
        "kpax_discipline_selector: picked %d disciplines (%s) — %s",
        agent_count,
        [d.name_en for d in picked],
        rationale,
    )
    return picked, agent_count
