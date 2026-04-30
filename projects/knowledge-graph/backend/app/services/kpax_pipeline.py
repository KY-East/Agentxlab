"""KPAX v0 pipeline — orchestrates one KPAX decision request end-to-end.

Wires together:
  1. ``kpax_discipline_selector.select_disciplines`` — picks 3 / 5 / 7 disciplines
  2. Creates ``Debate`` + ``DebateAgent`` rows in the **AXL main DB**
     (not the experiment isolated copy; spec §8.3)
  3. ``debate_engine.generate_agents`` — builds agent system prompts
  4. ``debate_engine.run_round`` × N — actual multi-agent debate
  5. ``debate_engine.generate_summary`` — moderator 四段中文总结
  6. Assembles ``KpaxDebateResult`` for the renderer layer

**AXL vs KPAX boundary** (Ken 硬规则 #6):
  This service lives inside the AXL codebase (``projects/knowledge-graph/backend/``),
  so it is allowed to ``import`` AXL internals directly. The HTTP boundary
  AXL ↔ KPAX is the ``kpax_router.py`` endpoint layer — KPAX backend
  (``kpax/backend/``) only speaks HTTP to those endpoints.

**wallet_address scope decision** (cursor 2026-04-17, pending @cc PR review):
  PRD §13.4 says all v0 new code uses ``wallet_address``. Scope chosen: NARROW.
  - External KPAX-facing schema + this pipeline + token_ledger use ``wallet_address``
  - AXL internals (``chat_completion(..., user_id: int)``, ``token_quota``,
    ``users`` FK) stay ``user_id`` — they are bound to AXL ``users`` table.
  - v0 KPAX requests do NOT flow through AXL auth, so ``user_id=None`` is
    always passed downstream. When v1 introduces wallet→user mapping this
    becomes a lookup, but v0 decoupling stays clean.
  Flagged in this docstring so @cc / @codex can push back if wrong.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from app.models.debate import Debate, DebateAgent
from app.models.discipline import Discipline
from app.services.debate_engine import (
    assign_models_to_agents,
    generate_agents,
    generate_summary,
    run_round,
    run_round_stream,
)
from app.services.kpax_discipline_selector import select_disciplines

logger = logging.getLogger(__name__)

# PRD §13.3 §3 — v1.3 depth map (deep = 5 rounds, 6+ reserved for research SKU)
DEPTH_TO_ROUNDS: dict[str, int] = {"quick": 2, "standard": 4, "deep": 5}

# v0 cost model — rough estimate per round per agent. Refined in v0.1 when
# ``chat_completion`` returns real token usage. Numbers calibrated against
# experiments/emergence_decomposition cost data (mean $0.99/standard debate
# with 7 agents × 4 rounds ≈ $0.035/agent-round).
_COST_PER_AGENT_ROUND_USD: float = 0.035

# v0 rough token accounting (actual usage not exposed by chat_completion).
# Updated to real numbers in v0.1 when we surface LiteLLM response.usage.
_TOKEN_IN_PER_AGENT_ROUND: int = 3000
_TOKEN_OUT_PER_AGENT_ROUND: int = 2000


class KpaxNotImplementedV0(Exception):
    """Raised when a v1+ feature is requested against a v0 endpoint.

    The router maps this to HTTP 501 ``not_implemented_in_v0``.
    """


class KpaxPipelineError(Exception):
    """Raised when the KPAX debate pipeline fails before a usable result."""


@dataclass
class ExpertLensInfo:
    """One seat in the debate (moderator excluded).

    ``expert_key`` format (PRD §13.3 §8.2):
      - v0: ``debate_{debate_id}_agent_{agent_id}`` (this class always emits this)
      - v1: ``skill_{skill_id}`` (platform skill avatars — not v0)

    Schema regex ``^(debate_\\d+_agent_\\d+|skill_[a-z0-9_]+)$`` is enforced
    at the router layer.
    """

    expert_key: str
    discipline_id: int
    name_en: str
    name_zh: str
    skill_source: str  # v0 always "platform_discipline"


@dataclass
class KpaxDebateResult:
    debate_id: int
    expert_lenses: list[ExpertLensInfo]
    rounds: int
    depth: str
    summary: dict[str, str]  # consensus / disagreements / open_questions / directions
    token_usage: dict[str, int] = field(default_factory=dict)
    cost_usd: float = 0.0
    wallet_address: str | None = None


def _validate_depth(depth: str) -> int:
    rounds = DEPTH_TO_ROUNDS.get(depth)
    if rounds is None:
        raise ValueError(
            f"invalid_depth: {depth!r} not in {list(DEPTH_TO_ROUNDS.keys())}"
        )
    return rounds


def _enforce_v0_constraints(llm_provider_override: dict | None) -> None:
    """Gate v1-only features behind explicit 501.

    v0 must reject non-null ``llm_provider_override`` (BYOM ships v1, spec §13.3 §9).
    """
    if llm_provider_override is not None:
        raise KpaxNotImplementedV0(
            "llm_provider_override=non-null not supported in v0; BYOM scheduled v1"
        )


def _create_debate_row(
    question: str,
    depth: str,
    disciplines: list[Discipline],
    db: Session,
) -> Debate:
    """Create the Debate row and attach disciplines.

    KPAX 统一用 ``mode="debate"`` + ``proposition=question`` —— 这让
    ``generate_agents`` 给每个学科打 ``discipline_advocate`` stance，触发
    跨学科碰撞（而非自由讨论）。
    """
    debate = Debate(
        title=question[:500],
        mode="debate",
        proposition=question,
        language="zh",
        depth=depth,
        status="active",
        created_by=None,  # v0 KPAX 不接 AXL 订阅体系 (see module docstring)
    )
    debate.disciplines.extend(disciplines)
    db.add(debate)
    db.flush()
    return debate


async def _build_and_persist_agents(
    debate: Debate,
    disciplines: list[Discipline],
    question: str,
    db: Session,
) -> None:
    """Call ``generate_agents`` + persist ``DebateAgent`` rows.

    **KPAX 产品约定**：每学科 1 位化身 (席位 = 学科数 = 3 / 5 / 7)。
    传 ``user_weights = {d.id: 30}`` 让 ``_decide_team_sizes`` 走 size=1 分支
    (见 debate_engine._decide_team_sizes：weight < 40 → team_size=1)。
    否则 default weight=50 会给每学科 2 agent，席位数翻倍，违反产品约定。
    """
    user_weights = {d.id: 30 for d in disciplines}
    agent_specs = await generate_agents(
        disciplines=disciplines,
        mode="debate",
        proposition=question,
        user_weights=user_weights,
        language="zh",
        user_id=None,
        db=db,
    )
    for spec in agent_specs:
        agent = DebateAgent(
            debate_id=debate.id,
            agent_name=spec["agent_name"],
            discipline_id=spec["discipline_id"],
            persona=spec["persona"],
            rank=spec["rank"],
            weight=spec["weight"],
            stance=spec["stance"],
            system_prompt=spec["system_prompt"],
            sort_order=spec["sort_order"],
        )
        db.add(agent)
    db.flush()
    db.refresh(debate)


def _build_expert_lenses(debate: Debate) -> list[ExpertLensInfo]:
    """Construct expert_lenses from persisted DebateAgent rows.

    Moderator is excluded (KPAX 席位口径 = 学科化身数，不含主持人，见
    notes/design.md §3 时间博物馆场景 + KPAX.md 化身体系)。

    Every returned lens carries:
      - ``expert_key`` = ``debate_{debate_id}_agent_{agent_id}`` (PRD §13.3 §8.2)
      - ``skill_source`` = ``"platform_discipline"`` (PRD §13.3 §8.x; v0 唯一值)
      - ``name_zh`` (PRD §13.3 §8.2 新增字段，前端 zh 显示)
    """
    lenses: list[ExpertLensInfo] = []
    for agent in debate.agents:
        if agent.persona == "moderator":
            continue
        if agent.discipline_id is None or agent.discipline is None:
            continue
        disc = agent.discipline
        lenses.append(
            ExpertLensInfo(
                expert_key=f"debate_{debate.id}_agent_{agent.id}",
                discipline_id=disc.id,
                name_en=disc.name_en,
                name_zh=disc.name_zh or disc.name_en,
                skill_source="platform_discipline",
            )
        )
    return lenses


def _estimate_cost(rounds: int, agent_count: int) -> tuple[dict[str, int], float]:
    """v0 rough cost proxy — LiteLLM usage not surfaced through chat_completion yet.

    Returns ({input_tokens, output_tokens}, cost_usd).
    Replaced with real accounting in v0.1 (requires chat_completion patch).
    """
    speaking_agents = agent_count + 1  # + moderator
    total_input = _TOKEN_IN_PER_AGENT_ROUND * speaking_agents * rounds
    total_output = _TOKEN_OUT_PER_AGENT_ROUND * speaking_agents * rounds
    cost = round(_COST_PER_AGENT_ROUND_USD * speaking_agents * rounds, 4)
    return {"input": total_input, "output": total_output}, cost


async def run_kpax_debate(
    question: str,
    user_context: dict[str, Any],
    depth: str,
    db: Session,
    *,
    wallet_address: str | None = None,
    llm_provider_override: dict | None = None,
) -> KpaxDebateResult:
    """Synchronous (non-streaming) end-to-end KPAX debate run.

    SSE variant lives in ``stream_kpax_debate`` (step 10, same module).

    Raises:
        KpaxNotImplementedV0: on v1-only request fields
        ValueError: on invalid depth
        KpaxPipelineError: when debate engine fails mid-run
    """
    _enforce_v0_constraints(llm_provider_override)
    rounds = _validate_depth(depth)

    disciplines, agent_count = await select_disciplines(
        question, user_context, db, user_id=None,
    )
    logger.info(
        "kpax_pipeline: selected %d disciplines for question=%r depth=%s wallet=%s",
        agent_count, question[:60], depth, wallet_address,
    )

    debate = _create_debate_row(question, depth, disciplines, db)
    await _build_and_persist_agents(debate, disciplines, question, db)
    assign_models_to_agents(list(debate.agents), db)

    try:
        for r in range(rounds):
            await run_round(debate, db, user_id=None)
            logger.info("kpax_pipeline: debate %d round %d/%d done",
                        debate.id, r + 1, rounds)
    except Exception as exc:
        debate.status = "failed"
        db.flush()
        db.commit()
        raise KpaxPipelineError(f"debate_failed: {exc}") from exc

    try:
        summary = await generate_summary(debate, db, user_id=None)
    except Exception as exc:
        raise KpaxPipelineError(f"summary_failed: {exc}") from exc

    lenses = _build_expert_lenses(debate)
    token_usage, cost_usd = _estimate_cost(rounds, agent_count)

    db.commit()
    logger.info(
        "kpax_pipeline: debate %d complete — %d rounds, %d lenses, est cost $%.4f",
        debate.id, rounds, len(lenses), cost_usd,
    )

    return KpaxDebateResult(
        debate_id=debate.id,
        expert_lenses=lenses,
        rounds=rounds,
        depth=depth,
        summary=summary,
        token_usage=token_usage,
        cost_usd=cost_usd,
        wallet_address=wallet_address,
    )


# ---------- SSE streaming variant (step 10) ----------

async def stream_kpax_debate_events(
    question: str,
    user_context: dict[str, Any],
    depth: str,
    db: Session,
    *,
    wallet_address: str | None = None,
    llm_provider_override: dict | None = None,
) -> AsyncIterator[tuple[str, dict[str, Any], KpaxDebateResult | None]]:
    """Streaming pipeline for SSE endpoints (PRD §13.3 §10 — mandatory v0).

    Yields ``(event_type, payload, final_result)`` tuples. The router wraps
    each tuple into an SSE frame. ``final_result`` is populated only on the
    very last ``summary_ready`` event so the router can run ``render_*`` and
    emit a ``final`` event with the full Response JSON.

    Event types:
      - ``agents_ready``   : {debate_id, expert_lenses}
      - ``round_start``    : {round, max_rounds}
      - ``message``        : {round, agent_id, agent_name, expert_key, content}
      - ``round_end``      : {round}
      - ``summary_ready``  : {summary, cost_usd}  + KpaxDebateResult in tuple[2]
      - ``error``          : router translates exceptions into this
    """
    _enforce_v0_constraints(llm_provider_override)
    rounds = _validate_depth(depth)

    disciplines, agent_count = await select_disciplines(
        question, user_context, db, user_id=None,
    )

    debate = _create_debate_row(question, depth, disciplines, db)
    await _build_and_persist_agents(debate, disciplines, question, db)
    assign_models_to_agents(list(debate.agents), db)

    lenses = _build_expert_lenses(debate)
    yield (
        "agents_ready",
        {
            "debate_id": debate.id,
            "expert_lenses": [
                {
                    "expert_key": l.expert_key,
                    "discipline_id": l.discipline_id,
                    "name_en": l.name_en,
                    "name_zh": l.name_zh,
                    "skill_source": l.skill_source,
                }
                for l in lenses
            ],
            "rounds_planned": rounds,
        },
        None,
    )

    agent_by_id = {a.id: a for a in debate.agents}

    try:
        for r in range(rounds):
            yield ("round_start", {"round": r + 1, "max_rounds": rounds}, None)
            async for msg in run_round_stream(debate, db, user_id=None):
                agent = agent_by_id.get(msg.agent_id) if msg.agent_id else None
                expert_key = (
                    f"debate_{debate.id}_agent_{msg.agent_id}"
                    if msg.agent_id
                    else None
                )
                yield (
                    "message",
                    {
                        "round": msg.round_number,
                        "agent_id": msg.agent_id,
                        "agent_name": agent.agent_name if agent else None,
                        "expert_key": expert_key,
                        "content": msg.content,
                    },
                    None,
                )
            yield ("round_end", {"round": r + 1}, None)
    except Exception as exc:
        debate.status = "failed"
        db.flush()
        db.commit()
        raise KpaxPipelineError(f"debate_failed: {exc}") from exc

    try:
        summary = await generate_summary(debate, db, user_id=None)
    except Exception as exc:
        raise KpaxPipelineError(f"summary_failed: {exc}") from exc

    token_usage, cost_usd = _estimate_cost(rounds, agent_count)
    result = KpaxDebateResult(
        debate_id=debate.id,
        expert_lenses=lenses,
        rounds=rounds,
        depth=depth,
        summary=summary,
        token_usage=token_usage,
        cost_usd=cost_usd,
        wallet_address=wallet_address,
    )
    db.commit()

    yield (
        "summary_ready",
        {"summary": summary, "cost_usd": cost_usd},
        result,
    )
