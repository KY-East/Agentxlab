"""Multi-agent academic debate engine.

Orchestrates agent generation, round-by-round debate, and structured summarisation.
"""
from __future__ import annotations

import json
import logging
import random

from sqlalchemy.orm import Session

from app.models.debate import Debate, DebateAgent, DebateMessage
from app.models.discipline import Discipline
from app.services.ai_provider import chat_completion
from app.config import settings

logger = logging.getLogger(__name__)

MAX_AGENTS = 8


def _get_model_pool() -> list[str]:
    """Collect available debate models from config, deduplicated."""
    pool: list[str] = []
    for m in (settings.debate_model_pro, settings.debate_model_con, settings.debate_model_moderator):
        if m and m not in pool:
            pool.append(m)
    return pool


def assign_models_to_agents(agents: list[DebateAgent], db: Session) -> None:
    """Randomly assign models to agents and persist to DB.

    Guarantees every model in the pool appears at least once.
    Skips agents that already have an assigned_model (idempotent).
    """
    pool = _get_model_pool()
    if not pool:
        return

    unassigned = [a for a in agents if not a.assigned_model]
    if not unassigned:
        return

    random.shuffle(unassigned)

    if len(pool) >= len(unassigned):
        for i, agent in enumerate(unassigned):
            agent.assigned_model = pool[i % len(pool)]
    else:
        already_used = {a.assigned_model for a in agents if a.assigned_model}
        missing = [m for m in pool if m not in already_used]

        seed_count = min(len(missing), len(unassigned))
        shuffled_missing = list(missing)
        random.shuffle(shuffled_missing)
        for i in range(seed_count):
            unassigned[i].assigned_model = shuffled_missing[i]

        for agent in unassigned[seed_count:]:
            agent.assigned_model = random.choice(pool)

    db.flush()


def _model_for_agent(agent: DebateAgent) -> str | None:
    """Return the model assigned to this agent, or None for default."""
    return agent.assigned_model or None
RANK_LABELS = {
    "professor": {"en": "Professor", "zh": "教授", "prefix": "Prof."},
    "associate": {"en": "Associate Professor", "zh": "副教授", "prefix": "Assoc. Prof."},
    "assistant": {"en": "Assistant Professor", "zh": "助理教授", "prefix": "Asst. Prof."},
}


def _zep_available() -> bool:
    try:
        from app.services.zep_manager import get_zep_client  # noqa: F401
        return True
    except Exception:
        return False

PERSONAS: list[dict] = [
    {
        "key": "pioneer",
        "label_en": "Pioneer",
        "label_zh": "开拓型",
        "desc_en": "Bold and visionary. Propose unconventional ideas, draw surprising cross-field connections, push toward novel territory.",
        "desc_zh": "大胆前瞻。提出非常规想法，建立跨领域的意外联系，推动讨论进入新领域。",
    },
    {
        "key": "rigorous",
        "label_en": "Rigorous",
        "label_zh": "严谨型",
        "desc_en": "Evidence-driven and meticulous. Insist on logical consistency, cite concrete studies and data, challenge unsupported claims.",
        "desc_zh": "以证据驱动，注重逻辑一致性，引用具体研究和数据，质疑缺乏支撑的观点。",
    },
    {
        "key": "pragmatic",
        "label_en": "Pragmatic",
        "label_zh": "实用型",
        "desc_en": "Focus on real-world applicability. Ask 'How to implement?' and 'Who benefits?'. Bridge theory and practice.",
        "desc_zh": "聚焦现实应用。关注'如何落地'和'谁受益'，在理论与实践之间架桥。",
    },
    {
        "key": "skeptic",
        "label_en": "Skeptic",
        "label_zh": "批判型",
        "desc_en": "Devil's advocate. Question assumptions, identify weaknesses, stress-test proposals. Constructively critical.",
        "desc_zh": "扮演质疑者。追问假设前提，识别弱点，压力测试方案。建设性地批判。",
    },
]

MODERATOR_PROMPTS = {
    "en": (
        "You are the Moderator of an interdisciplinary academic debate.\n"
        "- Synthesize perspectives from all participants\n"
        "- Identify emerging consensus and unresolved tensions\n"
        "- Guide the discussion toward productive research directions\n"
        "- Remain neutral — do not favour any discipline or stance\n\n"
        "Respond ONLY in English. Use bullet points. Be concise but insightful."
    ),
    "zh": (
        "你是一场跨学科学术辩论的主持人。\n"
        "- 综合所有参与者的观点\n"
        "- 识别正在形成的共识和未解决的分歧\n"
        "- 引导讨论朝有成效的研究方向推进\n"
        "- 保持中立，不偏向任何学科或立场\n\n"
        "只用中文回复。使用要点列表（bullet points）格式。精练但有洞察。"
    ),
}

STANCE_PROMPTS = {
    "discipline_advocate": {
        "en": (
            "You represent the perspective of YOUR discipline on this proposition. "
            "Argue WHY your field's methods, theories, and evidence are essential for understanding this topic. "
            "Challenge other disciplines' blind spots — point out what THEY miss that YOUR field captures. "
            "Defend your discipline's unique contribution when others question it."
        ),
        "zh": (
            "你代表你所在学科的视角来看待这个命题。"
            "论证为什么你的领域的方法论、理论和证据对于理解这个话题不可或缺。"
            "质疑其他学科的盲区——指出他们遗漏了什么，而你的学科能捕捉到什么。"
            "当其他学科质疑你时，捍卫你的学科的独特贡献。"
        ),
    },
}

ROUND_OPENERS = {
    1: {
        "en": (
            "Round 1 — Opening Positions. Present YOUR DISCIPLINE's unique perspective:\n"
            "- Your discipline's core thesis on this topic (1 sentence)\n"
            "- 2-3 key arguments: what does YOUR field see that others don't? Cite specific theories, methods, or findings.\n"
            "- Directly challenge another discipline's likely blind spot — what are they probably going to miss?\n"
            "- Pose 1 pointed question to a SPECIFIC other discipline in this debate."
        ),
        "zh": (
            "第 1 轮 —— 学科立场陈述。从你的学科视角出发：\n"
            "- 你的学科对这个话题的核心论点（1句话）\n"
            "- 2-3 个关键论据：你的领域能看到什么别人看不到的？引用具体的理论、方法或研究发现。\n"
            "- 直接指出另一个学科可能存在的盲区——他们大概率会忽略什么？\n"
            "- 向辩论中的某一个具体学科提出 1 个尖锐问题。"
        ),
    },
    2: {
        "en": (
            "Round 2 — Interdisciplinary Clash. Directly engage with other disciplines:\n"
            "- Respond to challenges aimed at YOUR discipline — defend or concede with evidence\n"
            "- Attack 1-2 specific claims from OTHER disciplines — explain why their framework is insufficient\n"
            "- Identify 1 point where another discipline complements yours (be specific about the mechanism)\n"
            "- Propose how YOUR discipline's methods could resolve a gap exposed by the debate"
        ),
        "zh": (
            "第 2 轮 —— 跨学科交锋。直接与其他学科碰撞：\n"
            "- 回应其他学科对你的质疑——用证据反驳或坦然承认不足\n"
            "- 攻击其他学科的 1-2 个具体论点——解释为什么他们的框架不够\n"
            "- 找出 1 个其他学科与你互补的点（具体说明怎么互补）\n"
            "- 提出你的学科方法如何能填补辩论中暴露的某个空白"
        ),
    },
    3: {
        "en": (
            "Round 3 — Integration & Boundaries. Final response:\n"
            "- What did other disciplines teach you that YOUR field alone could not see?\n"
            "- Where does your discipline's contribution START and END — be honest about your boundaries\n"
            "- Propose 1 concrete cross-disciplinary research design that combines insights from this debate\n"
            "- Name the single biggest remaining disagreement between disciplines and why it matters"
        ),
        "zh": (
            "第 3 轮 —— 整合与边界。最终发言：\n"
            "- 其他学科让你看到了什么你自己领域看不到的东西？\n"
            "- 你的学科贡献的边界在哪里——诚实地说你的局限\n"
            "- 提出 1 个结合本次辩论各方洞察的具体跨学科研究方案\n"
            "- 指出学科间目前最大的未解决分歧是什么，为什么它重要"
        ),
    },
}

DEFAULT_ROUND_OPENER = {
    "en": "Continue the discussion. Respond to the latest arguments using bullet points.",
    "zh": "继续讨论。用要点回应最新论点。",
}


def _build_agent_system_prompt(
    discipline_name: str,
    persona: dict,
    rank: str,
    weight: int,
    mode: str,
    stance: str | None,
    all_discipline_names: list[str],
    proposition: str | None,
    language: str = "zh",
    teammate_name: str | None = None,
) -> str:
    lang = language
    topic = " x ".join(all_discipline_names)
    rank_info = RANK_LABELS.get(rank, RANK_LABELS["professor"])
    is_senior = rank == "professor"
    word_limit = "150-250" if is_senior else "100-180"

    other_disciplines = [n for n in all_discipline_names if n != discipline_name]
    others_str = "、".join(other_disciplines)
    others_str_en = ", ".join(other_disciplines)

    if lang == "zh":
        core_hint = "你的学科是本次辩论的**核心方向**。" if weight >= 40 else "你的学科提供**辅助视角**。"
        persona_desc = persona.get("desc_zh", persona.get("desc", ""))
        parts = [
            f"你是{rank_info['zh']}，专攻 **{discipline_name}**，参与一场跨学科学术辩论。",
            f"参与辩论的学科有：{topic}。",
            f"\n## 你的使命\n你代表 **{discipline_name}** 参战。你的对手是来自 **{others_str}** 的学者。",
            f"你需要证明你的学科视角对这个问题不可或缺，同时直接质疑其他学科的局限性。",
            f"\n## 学术定位\n{core_hint}",
        ]
        if proposition:
            if mode == "debate":
                parts.append(f'\n## 命题\n"{proposition}"')
            else:
                parts.append(
                    f'\n## 核心问题\n本次讨论要解决的核心问题是：**"{proposition}"**\n'
                    f"你的所有发言都必须围绕这个问题展开。从 **{discipline_name}** 的角度出发，"
                    f"提供其他学科无法提供的方法论、关键变量、分析框架或可操作的建议。"
                )
        if teammate_name:
            if is_senior:
                parts.append(f"\n## 同学科队友\n**{teammate_name}** 是你的同学科队友。你们是一队的，共同捍卫 {discipline_name} 的立场。你可以补充或深化他的观点。")
            else:
                parts.append(f"\n## 同学科队友\n**{teammate_name}** 是你的资深同学科队友。你们是一队的。你可以从不同角度补充、或提出他未涉及的细节。")
        parts.append(f"\n## 讨论风格\n{persona_desc}")
        if mode == "debate" and stance and stance in STANCE_PROMPTS:
            parts.append(f"\n## 立场\n{STANCE_PROMPTS[stance]['zh']}")
        parts.append(
            f"\n## 输出规则\n"
            f"- 只用**中文**回复\n"
            f"- 使用**要点列表**（bullet points）格式，不写长段落\n"
            f"- 引用你学科的具体理论、学者或研究发现\n"
            f"- **必须点名回应**其他学科的具体论点——赞同、反驳或发展\n"
            f"- **严禁复述本轮他人已提过的论点或角度**；要回应就必须**升级、反驳或补新证据**，不是换个说法重复\n"
            f"- **严禁凑字数**：宁可短而锐利，不要长而啰嗦。只说本轮有增量的内容\n"
            f"- 每次发言结尾：你的学科对核心问题的独特贡献是什么，其他学科做不到的"
        )
    else:
        core_hint = "Your discipline is a **core direction** in this debate." if weight >= 40 else "Your discipline provides a **supporting perspective**."
        persona_desc = persona.get("desc_en", persona.get("desc", ""))
        parts = [
            f"You are a {rank_info['en']} specializing in **{discipline_name}**, in an interdisciplinary academic debate.",
            f"Disciplines in this debate: {topic}.",
            f"\n## Your Mission\nYou represent **{discipline_name}**. Your opponents are scholars from **{others_str_en}**.",
            f"Prove that YOUR discipline's perspective is indispensable for this topic, while directly challenging the limitations of other disciplines.",
            f"\n## Standing\n{core_hint}",
        ]
        if proposition:
            if mode == "debate":
                parts.append(f'\n## Proposition\n"{proposition}"')
            else:
                parts.append(
                    f'\n## Core Question\nThe central question of this discussion is: **"{proposition}"**\n'
                    f"ALL your contributions must directly address this question. From **{discipline_name}**'s perspective, "
                    f"provide methodologies, variables, frameworks, or insights that OTHER disciplines cannot offer."
                )
        if teammate_name:
            if is_senior:
                parts.append(f"\n## Teammate\n**{teammate_name}** is your same-discipline teammate. You are on the same side, defending {discipline_name}'s position together. Build on or deepen their points.")
            else:
                parts.append(f"\n## Teammate\n**{teammate_name}** is your senior same-discipline teammate. You are allies. Supplement with new angles or details they didn't cover.")
        parts.append(f"\n## Style\n{persona_desc}")
        if mode == "debate" and stance and stance in STANCE_PROMPTS:
            parts.append(f"\n## Stance\n{STANCE_PROMPTS[stance]['en']}")
        parts.append(
            f"\n## Output Rules\n"
            f"- Respond ONLY in **English**\n"
            f"- Use **bullet points** — no long paragraphs\n"
            f"- Cite specific theories, scholars, or findings from your discipline\n"
            f"- **You MUST name and respond to** specific arguments from OTHER disciplines — agree, refute, or extend\n"
            f"- End each response: what is YOUR discipline's unique contribution that no other field can provide?"
        )
    return "\n".join(parts)


def _load_agent_cognition(
    discipline_id: int, rank: str, debate_topic: str, discipline_name: str,
) -> str | None:
    """Best-effort load of agent's accumulated cognition from Zep."""
    if not _zep_available():
        return None
    try:
        from app.services.agent_memory import format_agent_cognition_for_prompt
        return format_agent_cognition_for_prompt(
            discipline_id, rank, debate_topic, discipline_name,
        )
    except Exception as exc:
        logger.warning("Failed to load agent cognition for disc=%d rank=%s: %s",
                       discipline_id, rank, exc)
        return None


async def _resolve_weights(
    disciplines: list[Discipline],
    user_weights: dict[int, int] | None,
    proposition: str | None,
    user_id: int | None = None,
    db: Session | None = None,
) -> dict[int, int]:
    """Determine weight for each discipline: user-specified > LLM-inferred > equal."""
    weights: dict[int, int] = {}
    unresolved: list[Discipline] = []

    for d in disciplines:
        if user_weights and d.id in user_weights:
            weights[d.id] = max(0, min(100, user_weights[d.id]))
        else:
            unresolved.append(d)

    if not unresolved:
        return weights

    try:
        names_str = ", ".join(d.name_en for d in unresolved)
        all_names = ", ".join(d.name_en for d in disciplines)
        context = f"topic: {proposition}" if proposition else f"disciplines: {all_names}"
        prompt = (
            f"Given an interdisciplinary debate involving: {all_names}\n"
            f"Context: {context}\n\n"
            f"Rate the centrality of each of these disciplines to the debate "
            f"on a scale of 0-100: {names_str}\n\n"
            f"Respond ONLY with a JSON object mapping discipline name to weight, e.g. "
            f'{{"Computer Science": 70, "Psychology": 45}}'
        )
        raw = await chat_completion(
            [{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=300,
            user_id=user_id,
            db=db,
        )
        start = raw.index("{")
        end = raw.rindex("}") + 1
        parsed = json.loads(raw[start:end])
        name_to_id = {d.name_en: d.id for d in unresolved}
        for name, w in parsed.items():
            did = name_to_id.get(name)
            if did is not None:
                weights[did] = max(0, min(100, int(w)))
    except Exception as exc:
        logger.warning("LLM weight inference failed, using equal weights: %s", exc)

    for d in unresolved:
        if d.id not in weights:
            weights[d.id] = 50

    return weights


def _decide_team_sizes(
    disciplines: list[Discipline],
    weights: dict[int, int],
) -> dict[int, int]:
    """Return team size per discipline (1 or 2) respecting MAX_AGENTS cap."""
    sizes: dict[int, int] = {}
    for d in disciplines:
        sizes[d.id] = 2 if weights.get(d.id, 50) >= 40 else 1

    total = sum(sizes.values())
    if total > MAX_AGENTS:
        by_weight = sorted(disciplines, key=lambda d: weights.get(d.id, 50))
        for d in by_weight:
            if total <= MAX_AGENTS:
                break
            if sizes[d.id] == 2:
                sizes[d.id] = 1
                total -= 1

    return sizes


async def generate_agents(
    disciplines: list[Discipline],
    mode: str,
    proposition: str | None = None,
    *,
    user_weights: dict[int, int] | None = None,
    language: str = "zh",
    user_id: int | None = None,
    db: Session | None = None,
) -> list[dict]:
    """Build agent specs (not yet persisted). Returns list of dicts ready for DebateAgent creation."""
    lang = language
    names_en = [d.name_en for d in disciplines]
    names_display = [(d.name_zh or d.name_en) if lang == "zh" else d.name_en for d in disciplines]
    weights = await _resolve_weights(disciplines, user_weights, proposition, user_id=user_id, db=db)
    team_sizes = _decide_team_sizes(disciplines, weights)

    persona_pool = list(PERSONAS)
    random.shuffle(persona_pool)
    persona_idx = 0

    def next_persona() -> dict:
        nonlocal persona_idx
        p = persona_pool[persona_idx % len(persona_pool)]
        persona_idx += 1
        return p

    agent_specs: list[dict] = []
    order = 0

    disc_agent_names: dict[int, list[str]] = {}

    for disc in disciplines:
        size = team_sizes[disc.id]
        w = weights.get(disc.id, 50)
        zh = disc.name_zh or disc.name_en
        short = disc.name_en[:25]

        ranks = ["professor", "associate"] if size == 2 else ["professor"]
        team_names = [f"{RANK_LABELS[r]['prefix']} {short}" for r in ranks]
        disc_agent_names[disc.id] = team_names

        for j, rank in enumerate(ranks):
            persona = next_persona()
            stance: str | None = None
            if mode == "debate":
                stance = "discipline_advocate"

            disc_display = (disc.name_zh or disc.name_en) if lang == "zh" else disc.name_en
            teammate = team_names[1 - j] if size == 2 else None
            base_prompt = _build_agent_system_prompt(
                disc_display, persona, rank, w,
                mode, stance, names_display, proposition,
                language=lang,
                teammate_name=teammate,
            )

            cognition_block = _load_agent_cognition(
                disc.id, rank, " x ".join(names_en), disc.name_en,
            )
            full_prompt = (
                f"{base_prompt}\n\n{cognition_block}" if cognition_block else base_prompt
            )

            agent_specs.append({
                "agent_name": f"{RANK_LABELS[rank]['prefix']} {short} ({zh})",
                "discipline_id": disc.id,
                "persona": persona["key"],
                "rank": rank,
                "weight": w,
                "stance": stance,
                "system_prompt": full_prompt,
                "sort_order": order,
            })
            order += 1

    moderator_stance = "moderator" if mode == "debate" else None
    mod_name = "主持人 (跨学科综合)" if lang == "zh" else "Moderator (Interdisciplinary)"
    mod_prompt = MODERATOR_PROMPTS.get(lang, MODERATOR_PROMPTS["en"])
    if proposition:
        if lang == "zh":
            mod_prompt += f'\n\n本次讨论的核心问题是：**"{proposition}"**\n你的总结和引导必须围绕这个问题。每轮结束时，明确指出各学科对核心问题的具体贡献，以及还有哪些方面尚未回答。'
        else:
            mod_prompt += f'\n\nThe core question of this discussion is: **"{proposition}"**\nYour summaries and guidance must center on this question. At the end of each round, explicitly state each discipline\'s concrete contribution to answering the question, and what aspects remain unanswered.'
    agent_specs.append({
        "agent_name": mod_name,
        "discipline_id": None,
        "persona": "moderator",
        "rank": "professor",
        "weight": 0,
        "stance": moderator_stance,
        "system_prompt": mod_prompt,
        "sort_order": order,
    })

    return agent_specs


def _retrieve_zep_contexts(debate: Debate) -> tuple[str, dict[int, str]]:
    """Retrieve knowledge from Zep: 1 shared context + per-agent discipline context.

    Returns (shared_context, {agent.id: discipline_context}).
    Best-effort: returns empty strings if Zep unavailable.
    """
    if not _zep_available():
        return "", {}

    try:
        from app.services.zep_manager import retrieve_context
    except Exception:
        return "", {}

    topic = debate.title
    shared = retrieve_context(topic, limit=5)

    per_agent: dict[int, str] = {}
    for agent in debate.agents:
        if agent.discipline:
            ctx = retrieve_context(agent.discipline.name_en, limit=3)
            if ctx:
                per_agent[agent.id] = ctx

    return shared, per_agent


def _build_knowledge_message(shared: str, agent_specific: str | None) -> str | None:
    """Format Zep knowledge into a single context block for LLM injection."""
    parts = []
    if shared:
        parts.append(f"[Shared knowledge from the lab's knowledge base]\n{shared}")
    if agent_specific:
        parts.append(f"[Knowledge specific to your discipline]\n{agent_specific}")
    if not parts:
        return None
    return (
        "The following background knowledge has been retrieved from Agent X Lab's "
        "knowledge base. Use it to enrich your arguments where relevant, but do not "
        "simply repeat it.\n\n" + "\n\n".join(parts)
    )


def _order_agents_for_round(agents: list[DebateAgent], round_num: int) -> list[DebateAgent]:
    """Determine speaking order for a round.

    Round 1: Professors first (by sort_order), then juniors, then Moderator.
    Round 2+: Interleaved by discipline — Prof A, Prof B, Assoc A, Assoc B, then Moderator.
    """
    moderators = [a for a in agents if a.persona == "moderator"]
    professors = sorted(
        [a for a in agents if a.rank == "professor" and a.persona != "moderator"],
        key=lambda a: a.sort_order,
    )
    juniors = sorted(
        [a for a in agents if a.rank in ("associate", "assistant")],
        key=lambda a: a.sort_order,
    )

    if round_num == 1:
        return professors + juniors + moderators

    ordered: list[DebateAgent] = []
    max_len = max(len(professors), len(juniors))
    for i in range(max_len):
        if i < len(professors):
            ordered.append(professors[i])
        if i < len(juniors):
            ordered.append(juniors[i])
    return ordered + moderators


MAX_ROUNDS = 6


async def run_round(debate: Debate, db: Session, *, user_id: int | None = None) -> list[DebateMessage]:
    """Execute one round: each agent speaks in order, seeing full history."""
    msgs: list[DebateMessage] = []
    async for msg in run_round_stream(debate, db, user_id=user_id):
        msgs.append(msg)
    return msgs


async def run_round_stream(debate: Debate, db: Session, *, user_id: int | None = None):
    """Async generator that yields each DebateMessage as it is created.

    This powers both the batch ``run_round`` and the SSE endpoint so that
    the frontend can render agent responses one-by-one instead of waiting
    for the full round to finish.
    """
    current_round = 1
    if debate.messages:
        current_round = max(m.round_number for m in debate.messages) + 1

    if current_round > MAX_ROUNDS:
        raise ValueError(f"Maximum round limit ({MAX_ROUNDS}) reached")

    lang = getattr(debate, "language", "zh") or "zh"
    depth = getattr(debate, "depth", "standard") or "standard"

    from app.services.session_memory import build_compressed_context
    history = await build_compressed_context(
        list(debate.messages), current_round,
        depth=depth, language=lang, user_id=user_id, db=db,
    )

    opener_map = ROUND_OPENERS.get(current_round, DEFAULT_ROUND_OPENER)
    round_opener = opener_map.get(lang, opener_map.get("en", ""))

    if any(not a.assigned_model for a in debate.agents):
        assign_models_to_agents(list(debate.agents), db)
    model_info = {a.agent_name: a.assigned_model or "default" for a in debate.agents}
    logger.info("Debate %d round %d models: %s", debate.id, current_round, model_info)

    shared_ctx, per_agent_ctx = _retrieve_zep_contexts(debate)
    speaking_order = _order_agents_for_round(list(debate.agents), current_round)

    disc_names = [d.name_en for d in debate.disciplines]
    disc_name_to_id = {d.name_en: d.id for d in debate.disciplines}

    new_messages: list[DebateMessage] = []

    for agent in speaking_order:
        if agent.persona == "moderator" and current_round == 1:
            continue

        depth_tokens = {
            "quick":    (800, 600),
            "standard": (4000, 3000),
            "deep":     (8000, 6000),
            "max":      (12000, 10000),
        }
        prof_max, assoc_max = depth_tokens.get(depth, (4000, 3000))
        max_tokens = prof_max if agent.rank == "professor" else assoc_max

        messages = [
            {"role": "system", "content": agent.system_prompt},
        ]

        knowledge_msg = _build_knowledge_message(
            shared_ctx, per_agent_ctx.get(agent.id)
        )
        if knowledge_msg:
            messages.append({"role": "user", "content": knowledge_msg})

        messages.extend(history)
        messages.append({"role": "user", "content": round_opener})

        if new_messages:
            for nm in new_messages:
                messages.append({
                    "role": "assistant" if nm.agent_id == agent.id else "user",
                    "content": f"[{_agent_label(nm, debate)}]: {nm.content}",
                })

        agent_model = _model_for_agent(agent)
        content = await chat_completion(messages, model=agent_model, temperature=0.8, max_tokens=max_tokens, user_id=user_id, db=db)

        msg = DebateMessage(
            debate_id=debate.id,
            agent_id=agent.id,
            role="agent",
            content=content,
            round_number=current_round,
        )
        db.add(msg)
        db.flush()
        new_messages.append(msg)

        if agent.persona != "moderator":
            try:
                from app.services.spark_extractor import extract_sparks_from_message
                await extract_sparks_from_message(
                    message=msg,
                    agent=agent,
                    debate_discipline_names=disc_names,
                    discipline_name_to_id=disc_name_to_id,
                    db=db,
                    language=lang,
                    user_id=user_id,
                )
            except Exception as exc:
                logger.warning("Spark extraction failed for message %d: %s", msg.id, exc)

        yield msg

    db.flush()


async def generate_summary(debate: Debate, db: Session, *, user_id: int | None = None) -> dict[str, str]:
    """Generate structured four-part summary from the Moderator perspective."""
    lang = getattr(debate, "language", "zh") or "zh"
    history = _build_history(debate.messages)

    if lang == "zh":
        prompt = (
            "辩论已结束。作为主持人，用中文提供结构化总结（bullet points）：\n\n"
            "## 1. 共识\n参与者达成了哪些共识？\n\n"
            "## 2. 分歧\n哪些关键点仍有争议？\n\n"
            "## 3. 开放问题\n讨论中涌现了哪些新问题？\n\n"
            "## 4. 建议研究方向\n基于辩论，最有前景的具体研究方向是什么？\n\n"
            "只用中文回复。使用要点列表格式。保留上面的章节标题。"
        )
    else:
        prompt = (
            "The debate has concluded. As the Moderator, provide a structured summary in bullet points:\n\n"
            "## 1. Consensus\nWhat did participants agree on?\n\n"
            "## 2. Disagreements\nWhat key points remain contested?\n\n"
            "## 3. Open Questions\nWhat new questions emerged?\n\n"
            "## 4. Suggested Research Directions\n"
            "Based on the debate, what concrete research directions are most promising?\n\n"
            "Respond ONLY in English. Use bullet points. Keep the section headers exactly as shown."
        )

    mod_prompt = MODERATOR_PROMPTS.get(lang, MODERATOR_PROMPTS["en"])
    messages = [
        {"role": "system", "content": mod_prompt},
        *history,
        {"role": "user", "content": prompt},
    ]

    mod_agent = next((a for a in debate.agents if a.persona == "moderator"), None)
    mod_model = _model_for_agent(mod_agent) if mod_agent else None
    raw = await chat_completion(messages, model=mod_model, temperature=0.5, max_tokens=3000, user_id=user_id, db=db)
    sections = _parse_summary_sections(raw)

    debate.summary_consensus = sections.get("consensus", raw)
    debate.summary_disagreements = sections.get("disagreements", "")
    debate.summary_open_questions = sections.get("open_questions", "")
    debate.summary_directions = sections.get("directions", "")
    debate.status = "completed"
    db.flush()

    if _zep_available():
        try:
            from app.services.zep_manager import push_debate_summary
            disc_names = [d.name_en for d in debate.disciplines]
            push_debate_summary(
                debate_title=debate.title,
                disciplines=disc_names,
                mode=debate.mode,
                proposition=debate.proposition,
                consensus=debate.summary_consensus,
                disagreements=debate.summary_disagreements,
                open_questions=debate.summary_open_questions,
                directions=debate.summary_directions,
                debate_id=debate.id,
            )
        except Exception as e:
            logger.warning("Zep push after debate summary failed: %s", e)

        try:
            from app.services.cognition_distiller import distill_all_agents
            await distill_all_agents(debate, db, user_id=user_id)
        except Exception as e:
            logger.warning("Post-debate cognition distillation failed: %s", e)

    try:
        from app.services.experiment_tracker import record_experiment_meta
        record_experiment_meta(debate, db)
    except Exception as e:
        logger.warning("Experiment meta recording failed: %s", e)

    try:
        from app.services.forum_auto import auto_create_debate_post, highlight_top_sparks
        auto_create_debate_post(debate, db)
        highlight_top_sparks(debate.id, db)
    except Exception as e:
        logger.warning("Forum auto-post failed: %s", e)

    return sections


async def suggest_mode(discipline_names: list[str], *, user_id: int | None = None, db: Session | None = None) -> dict:
    """Ask the LLM which debate mode fits the given discipline combination."""
    prompt = (
        f"Given these academic disciplines: {', '.join(discipline_names)}\n\n"
        "Which format would be more productive for their interdisciplinary exchange?\n"
        "A) Free Discussion — open-ended exploration, each discipline shares perspectives freely\n"
        "B) Focused Debate — each discipline defends its own approach to a specific question, "
        "disciplines clash with each other (NOT for/against, but discipline-vs-discipline)\n\n"
        "Respond with ONLY a JSON object: "
        '{"mode": "free" or "debate", "reason_en": "...", "reason_zh": "...", '
        '"suggested_proposition": "..." (only if mode is debate — phrase it as a research question '
        'that each discipline would approach differently, NOT a yes/no proposition)}'
    )
    raw = await chat_completion(
        [{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500,
        user_id=user_id,
        db=db,
    )

    import json
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        return json.loads(raw[start:end])
    except (ValueError, json.JSONDecodeError):
        return {
            "mode": "free",
            "reason_en": "Free discussion recommended for broad exploration.",
            "reason_zh": "推荐自由讨论以进行广泛探索。",
            "suggested_proposition": None,
        }


def _build_history(messages: list[DebateMessage]) -> list[dict]:
    """Convert DB messages to LLM message format."""
    result = []
    for m in messages:
        if m.role == "agent" and m.agent:
            label = m.agent.agent_name
            result.append({"role": "user", "content": f"[{label}]: {m.content}"})
        elif m.role == "system":
            result.append({"role": "system", "content": m.content})
        elif m.role == "user":
            result.append({"role": "user", "content": m.content})
    return result


def _agent_label(msg: DebateMessage, debate: Debate) -> str:
    if msg.agent:
        return msg.agent.agent_name
    return "System"


def _parse_summary_sections(raw: str) -> dict[str, str]:
    """Best-effort parse of the four summary sections from markdown."""
    sections: dict[str, str] = {}
    current_key: str | None = None
    current_lines: list[str] = []

    key_map = {
        "consensus": "consensus",
        "共识": "consensus",
        "disagreement": "disagreements",
        "分歧": "disagreements",
        "open question": "open_questions",
        "开放问题": "open_questions",
        "suggested research": "directions",
        "建议研究方向": "directions",
        "research direction": "directions",
    }

    for line in raw.split("\n"):
        stripped = line.strip().lower()
        matched_key = None
        for trigger, key in key_map.items():
            if trigger in stripped and stripped.startswith("#"):
                matched_key = key
                break

        if matched_key:
            if current_key and current_lines:
                sections[current_key] = "\n".join(current_lines).strip()
            current_key = matched_key
            current_lines = []
        else:
            current_lines.append(line)

    if current_key and current_lines:
        sections[current_key] = "\n".join(current_lines).strip()

    return sections
