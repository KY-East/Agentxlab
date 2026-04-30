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


def _model_family(model: str | None) -> str:
    """Map a LiteLLM model slug to its provider family.

    Used by assign_models_to_agents to enforce "same discipline = different
    LLM family" (Phase 0 F), a lightweight diversity lever against the
    twin-output bug. See notes/research/agent-twin-fix-decision-gate.md.
    """
    if not model:
        return "unknown"
    m = model.lower()
    if m.startswith("anthropic/") or "claude" in m:
        return "anthropic"
    if m.startswith("openai/") or m.startswith("gpt-") or m.startswith("gpt"):
        return "openai"
    if m.startswith("deepseek/") or "deepseek" in m:
        return "deepseek"
    if m.startswith("gemini/") or "gemini" in m:
        return "google"
    if "/" in m:
        return m.split("/", 1)[0]
    return "other"


def assign_models_to_agents(agents: list[DebateAgent], db: Session) -> None:
    """Randomly assign models to agents and persist to DB.

    Guarantees every model in the pool appears at least once.
    Skips agents that already have an assigned_model (idempotent).

    Phase 0 F (2026-04-20): when a discipline has >= 2 agents and the model
    pool spans >= 2 families, enforce "same-discipline agents use different
    LLM families" to reduce twin-output collapse.
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

    # Phase 0 F: same-discipline-different-family enforcement
    _enforce_same_discipline_different_family(agents, pool)

    db.flush()


def _enforce_same_discipline_different_family(
    agents: list[DebateAgent], pool: list[str]
) -> None:
    """Swap models so no two same-discipline agents share a LLM family.

    Best-effort: if the pool only spans 1 family or a discipline has more
    agents than distinct families available, logs a warning and moves on
    (no swap possible). The moderator (discipline_id=None) is never touched.
    """
    pool_families = {_model_family(m) for m in pool}
    if len(pool_families) < 2:
        return

    by_disc: dict[int, list[DebateAgent]] = {}
    for a in agents:
        if a.discipline_id is None or a.persona == "moderator":
            continue
        by_disc.setdefault(a.discipline_id, []).append(a)

    for disc_id, team in by_disc.items():
        if len(team) < 2:
            continue
        families_used = [_model_family(a.assigned_model) for a in team]
        if len(set(families_used)) == len(team):
            continue

        # Conflict: try to swap one team member's model with an outside agent
        # whose family is different and whose new family won't create a
        # conflict in its own team.
        for i, member in enumerate(team):
            member_fam = _model_family(member.assigned_model)
            siblings_fams = {
                _model_family(x.assigned_model)
                for j, x in enumerate(team) if j != i
            }
            if member_fam not in siblings_fams:
                continue
            # Find a swap candidate outside this discipline
            outside = [
                x for x in agents
                if x.discipline_id != disc_id
                and x.persona != "moderator"
                and _model_family(x.assigned_model) != member_fam
                and _model_family(x.assigned_model) not in siblings_fams
            ]
            if not outside:
                logger.warning(
                    "F-constraint: discipline %d cannot resolve family conflict "
                    "(member=%s, siblings=%s); leaving as-is",
                    disc_id, member.assigned_model, families_used,
                )
                break
            swap = random.choice(outside)
            # Verify swap doesn't break swap's own team
            swap_siblings_fams = {
                _model_family(x.assigned_model)
                for x in agents
                if x.discipline_id == swap.discipline_id
                and x.id != swap.id
                and x.persona != "moderator"
            }
            if member_fam in swap_siblings_fams:
                continue
            member.assigned_model, swap.assigned_model = (
                swap.assigned_model, member.assigned_model,
            )
            logger.info(
                "F-constraint: swapped %s <-> %s to avoid same-family twins in disc %d",
                member.assigned_model, swap.assigned_model, disc_id,
            )
            break


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
        "You are the Director of an interdisciplinary debate — not a passive summarizer.\n"
        "Your single job: keep scholars answering the user's actual question, while protecting their freedom to be bold, speculative, and cross-disciplinary.\n\n"
        "Round 1 (opening): Quote the user's raw question verbatim first — this is what they really asked, keep their voice. Then briefly show the academic reframing and the per-discipline angle menu that were prepared beforehand. You are INTRODUCING the question and MAPPING available directions — you are NOT assigning tasks. Scholars pick what they want.\n"
        "Round 2+ (closing each round): Briefly name who answered the user's question and who drifted into discipline-survey mode. State in one line what the NEXT round should focus on. Surface bold or unexpected moves worth amplifying — reward imagination, not conformity.\n\n"
        "Tone: decisive, terse. You trust these scholars; you don't babysit them. Respond ONLY in English. Bullet points. No filler."
    ),
    "zh": (
        "你是一场跨学科辩论的**导演**——不是被动的总结员。\n"
        "你的唯一职责：让学者们真正回答用户的实际问题，同时保护他们大胆、思辨、跨学科的自由。\n\n"
        "Round 1（开场）：先**原话引用用户的问题**——这是他们真实的表达，保留他们的语气。然后简述已经准备好的学术化改写、以及每个学科可能切入的角度菜单。你只是在**介绍问题、展示方向地图**——**不是在派活**。学者自己决定切哪个角度。\n"
        "Round 2+（每轮末尾）：简短指出谁真在回答用户的问题、谁绕回了本学科的舒适区。用一句话说**下一轮应该聚焦什么**。把大胆或出人意料的想法挑出来放大——奖励想象力，不奖励循规蹈矩。\n\n"
        "语气：果断、简练。你信任这些学者，不替他们写作业。只用中文。要点列表，不灌水。"
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
            "Round 1 — Your turn. The Moderator has framed the question and given your discipline an angle.\n"
            "- **Open with a direct stab at the user's question** (1-3 sentences): what would YOUR field actually say / do / predict? Concrete, not a literature survey.\n"
            "- Then support it: 2-3 arguments drawing on your discipline's theories, methods, or evidence — cite specifics.\n"
            "- Challenge one blind spot of another discipline — what will they likely miss on THIS question?\n"
            "- Pose 1 pointed question to a specific other discipline.\n"
            "Be bold and speculative if your field supports it. Do not hedge into generalities."
        ),
        "zh": (
            "第 1 轮 —— 轮到你。主持人已经改写了问题，给你的学科指派了一个切入角度。\n"
            "- **开头直接给出你的学科对用户问题的回答**（1-3 句）：你的领域会怎么看、怎么做、怎么预测？要具体，不是文献综述。\n"
            "- 然后支撑它：2-3 个论据，用你学科的理论、方法或证据，点具体的名字。\n"
            "- 挑一个其他学科的盲区——他们在**这个问题上**可能漏掉什么？\n"
            "- 向某一个具体学科抛出 1 个尖锐问题。\n"
            "你的学科允许你大胆、思辨，就放开手。不要滑进空泛的概括。"
        ),
    },
    2: {
        "en": (
            "Round 2 — Clash. The Moderator just named who drifted and what the next round must chase.\n"
            "- **Sharpen or revise your answer to the user's question** in light of what you've heard (1-2 sentences up front).\n"
            "- Respond to challenges aimed at your discipline — defend or concede with evidence.\n"
            "- Attack 1-2 specific claims from other disciplines and explain why their framework falls short *on this question*.\n"
            "- Identify 1 point where another discipline complements you — be specific about the mechanism.\n"
            "- Propose how your methods could close a gap exposed in Round 1."
        ),
        "zh": (
            "第 2 轮 —— 交锋。主持人刚刚点名了谁偏了题 + 本轮应该聚焦什么。\n"
            "- **根据这一轮听到的，重新磨一遍你对用户问题的答案**（开头 1-2 句）。\n"
            "- 回应其他学科对你的质疑——用证据反驳或坦然承认不足。\n"
            "- 攻击其他学科的 1-2 个具体论点，解释为什么他们的框架**在这个问题上**不够。\n"
            "- 找出 1 个其他学科与你互补的点，具体说清互补机制。\n"
            "- 提出你的方法如何能填补第 1 轮暴露的某个空白。"
        ),
    },
    3: {
        "en": (
            "Round 3 — Your final move. Stop expanding disciplinary territory; converge to a minimal-runnable model.\n"
            "- **Deliver your final answer to the user's question** (2-4 sentences). Your sharpest, most committed version.\n"
            "- **Minimal-runnable model contribution (REQUIRED, Phase 2.5)**: from your discipline, fill in what you actually own:\n"
            "    - state variables (what the system tracks over time)\n"
            "    - observables (what can be measured / sampled)\n"
            "    - control variables (what an operator can set / tune)\n"
            "    - termination paths (how the system ends — endogenous collapse, external shock, exogenous shutdown, etc.)\n"
            "    - failure conditions (when does the model break / become unreliable)\n"
            "  Be specific to your discipline. Skip a field with one line if your discipline genuinely cannot contribute to it — better honest than padded.\n"
            "- What did other disciplines teach you that your field alone could not see?\n"
            "- Name where your contribution starts and ends — be honest about the boundary.\n"
            "- Name the single biggest unresolved disagreement and why it matters for the user."
        ),
        "zh": (
            "第 3 轮 —— 你的最后一步。**停止扩张学科领地，把贡献压到「最小可跑模型」的可裁决结构上**。\n"
            "- **给出你对用户问题的最终答案**（2-4 句）。最锐利、最坚定的版本。\n"
            "- **最小可跑模型贡献（Phase 2.5 必填）**：从你的学科出发，填你真正能贡献的部分：\n"
            "    - 状态变量（系统随时间跟踪的量）\n"
            "    - 可观测量（什么可以被测 / 采样）\n"
            "    - 控制变量（运营方能设 / 调的参数）\n"
            "    - 终止路径（系统怎么结束——内生崩盘 / 外部冲击 / 主动关停等）\n"
            "    - 失效条件（什么情况下模型不再可靠）\n"
            "  要具体到你的学科。某个字段你学科确实贡献不了就用一句话跳过——诚实比凑数好。\n"
            "- 其他学科让你看到了什么你自己领域看不到的东西？\n"
            "- 你的贡献从哪里开始、到哪里结束——诚实地说出边界。\n"
            "- 指出最大的未解决分歧是什么，以及为什么它对用户重要。"
        ),
    },
}

DEFAULT_ROUND_OPENER = {
    "en": "Continue the discussion. Respond to the latest arguments using bullet points.",
    "zh": "继续讨论。用要点回应最新论点。",
}

# Phase 1 (2026-04-24): FREE mode round openers — 建设性综合（库恩式），不是破坏性辩论。
# 产物：可跑的推演 spec（variables / assumptions / time_horizon / observables / falsification_conditions / next_steps 六字段）
# 裁定依据: notes/design.md #axl-debate-mode-design
# 硬规则（写进每轮 opener）:
# - R2/R3 agent 必须有"根本分歧"出口（防过度和谐）
# - R2 从"攻击其他学科"改为"建设性挑战"（指出变量缺失 / 假设漏洞 / 观测不可靠 / 失效条件）
# - R3 从"给最终答案"改为"给修正版六字段 spec"（非草案）
FREE_ROUND_OPENERS = {
    1: {
        "en": (
            "Round 1 — Open your discipline's angle on the user's question.\n"
            "- Start with 1-3 sentences of what YOUR discipline sees in this question — variables, mechanisms, time scale, observables it cares about.\n"
            "- Sketch 2-3 assumptions YOUR discipline would bring in, and at least one assumption you'd need from OTHER disciplines.\n"
            "- Name 1-2 concrete dimensions where you expect OTHER disciplines will fill gaps your field can't.\n"
            "Goal this round: lay down your discipline's raw material so the group can co-build a runnable spec by Round 3. Be concrete, not a literature survey. No need to attack anyone yet."
        ),
        "zh": (
            "第 1 轮 —— 从你学科的视角开场。\n"
            "- 用 1-3 句说你的学科在这个问题上看到什么——关心哪些变量 / 机制 / 时间尺度 / 可观测量。\n"
            "- 列出你学科会带进来的 2-3 条假设，以及至少 1 条你需要其他学科提供的假设。\n"
            "- 点 1-2 个维度，说明你预期其他学科能补上你学科填不了的缺口。\n"
            "本轮目标：把你学科的原材料摆出来，让讨论组到第 3 轮能共同交付一份可跑的 spec。要具体，不是文献综述。还不用攻击谁。"
        ),
    },
    2: {
        "en": (
            "Round 2 — Constructive challenge (NOT attack). You've heard everyone's Round 1.\n"
            "- **Pick 2-3 specific points from OTHER disciplines** and do constructive challenge: missing variable? fragile assumption? unreliable observable? failure condition they didn't name?\n"
            "- **Propose how to fix each challenge**: either plug in your discipline's variable/assumption, or flag it as needing more work.\n"
            "- Identify 1 point where YOUR discipline needs to revise based on what others said.\n"
            "- **Fundamental-disagreement exit**: if another discipline's assumption is, from your field's view, *fundamentally incompatible* with the problem — do NOT force-synthesize to be polite. Flag it as **根本分歧 / fundamental disagreement**, say why it can't enter your model, hand it to the moderator.\n"
            "Goal: refine raw material toward a shared spec. Disagreements that CAN be composed → compose; disagreements that CANNOT → flag, don't paper over."
        ),
        "zh": (
            "第 2 轮 —— **建设性挑战**（不是攻击）。你已经听过其他人第 1 轮的发言。\n"
            "- **挑 2-3 个其他学科的具体论点**做建设性挑战：哪个变量缺失？哪条假设脆弱？哪个观测不可靠？哪个失效条件他们没提？\n"
            "- **对每条挑战提出修正建议**：要么用你学科的变量 / 假设接上去，要么标出需要进一步工作。\n"
            "- 找 1 个你学科自己需要根据其他人发言**修正**的点。\n"
            "- **根本分歧出口**：如果你发现其他学科的假设在你学科看来**从根本上不成立**，不要为了协作而强行接入。请标注为「**根本分歧**」，说明它为什么不能进入你的模型，并交给 moderator 在合成阶段保留。\n"
            "本轮目标：把原材料加工得更接近可共用的 spec。能合成的分歧 → 合成；不能合成的 → 标出来，不要为了协作糊过去。"
        ),
    },
    3: {
        "en": (
            "Round 3 — Hand in YOUR discipline's **revised** contribution to the shared spec. NOT a draft, not a hedged survey — your refined position after Rounds 1-2.\n"
            "Structure it against these six fields (not every field applies equally to your discipline — fill what you can):\n"
            "1. **variables** — key variables YOUR discipline contributes (1-3 items).\n"
            "2. **assumptions** — assumptions YOU bring + which ones depend on OTHER disciplines.\n"
            "3. **time_horizon** — the time scale at which your variables are meaningful (hours? years?).\n"
            "4. **observables** — what can be measured to validate YOUR part, and at what confidence.\n"
            "5. **falsification_conditions** — under what observed result would YOUR contribution be proven wrong or off-scope.\n"
            "6. **next_steps** — 1-2 concrete next actions if we were to start executing this spec tomorrow.\n"
            "- At the end, list any **fundamental disagreements** with other disciplines you flagged in Round 2 that you still hold to.\n"
            "Goal: hand the moderator a runnable piece, not a statement of position. The moderator will compose; the user will fork this into the experiment board."
        ),
        "zh": (
            "第 3 轮 —— 交付你学科**修正后**的六字段贡献。**不是草案，不是带保留的综述**——是经过第 1-2 轮后你沉淀下来的最终版本。\n"
            "按以下六个字段组织（不是每个字段对你学科都同等适用——你能填的填）：\n"
            "1. **variables（变量）**—— 你学科贡献的关键变量（1-3 个）。\n"
            "2. **assumptions（假设）**—— 你带进来的假设 + 哪些依赖其他学科。\n"
            "3. **time_horizon（时间尺度）**—— 你的变量在什么时间尺度上有意义（小时？年？）。\n"
            "4. **observables（可观测量）**—— 可以测什么来验证你这部分，置信度多高。\n"
            "5. **falsification_conditions（证伪条件）**—— 观察到什么结果时，你的贡献会被证明是错的或超范围。\n"
            "6. **next_steps（下一步）**—— 如果明天就开始执行这份 spec，你会先做的 1-2 个具体动作。\n"
            "- 最后列出你在第 2 轮标过的、**坚持认为仍然成立**的所有「根本分歧」。\n"
            "本轮目标：给 moderator 交一份能跑的零件，不是一份立场声明。moderator 会做合成；用户会把这份 spec 叉进实验板块。"
        ),
    },
}

# Phase 1 (2026-04-24): FREE mode moderator — 协调者（Coordinator），不是导演（Director）。
# 行为分化:
# - 不评分、不点名"绕回舒适区"、不标"最有想象力"
# - 改为把讨论组织成「问题地图 / 可能路径 / 待验证假设 / 根本分歧保留 / 下一步推演」
# - 合成时必须保留冲突——不为统一而统一
# 裁定依据: notes/design.md #axl-debate-mode-design 硬规则第 3-4 条
FREE_MODERATOR_PROMPTS = {
    "en": (
        "You are the Coordinator of an interdisciplinary co-building session — NOT a judge, NOT a pressure-tester.\n"
        "The scholars in this room are working together to hand the user a runnable simulation spec, not a verdict.\n\n"
        "Round 1 (opening): Quote the user's raw question verbatim. Briefly show the academic reframing and per-discipline angle menu that were prepared. You are INTRODUCING and MAPPING — not assigning tasks.\n"
        "Round 2+ (closing each round): Organize what was said into FOUR layers: (1) **Question map** — what scholars agreed the question actually contains; (2) **Composable paths** — where disciplinary contributions plug into each other; (3) **Hypotheses to verify** — disagreements that can be resolved with evidence; (4) **Irreducible disagreements** — fundamental disagreements that scholars explicitly flagged. **DO NOT force-synthesize layer 4 into layer 2.** Preserve disagreements. Forced harmony produces a beautiful but boneless synthesis.\n"
        "End each closing with one line on what the NEXT round should chase — invitation, not assignment.\n\n"
        "Tone: coordinative, not judicial. You don't pick winners. You don't rank 'most imaginative'. Respond ONLY in English. Bullet points. No filler."
    ),
    "zh": (
        "你是一场跨学科**共建**研讨的**协调者**——不是裁判，不是压力测试员。\n"
        "在场学者是在协作给用户交付一份可跑的推演 spec，不是交付一份判决书。\n\n"
        "Round 1（开场）：先**原话引用用户的问题**。简述已经准备好的学术化改写和每学科的角度菜单。你在**介绍问题、展示方向**——不是在派活。\n"
        "Round 2+（每轮收尾）：把本轮发言组织成**四层**：(1) **问题地图**——学者们共识的「这个问题其实包含什么」；(2) **可合成路径**——学科贡献之间能接起来的部分；(3) **待验证假设**——能用证据解决的分歧；(4) **根本分歧**——学者明确标过的不能合成的分歧。**不要把第 4 层强行合成进第 2 层**。保留分歧。强行和谐只会产出一份漂亮但没骨头的综合。\n"
        "每轮收尾最后用一句话说下一轮可以推演什么——用邀请语气，不是派活。\n\n"
        "语气：协调性的，不是裁决性的。你不挑赢家。你不评「最有想象力」。只用中文。要点列表，不灌水。"
    ),
}

FREE_MODERATOR_ROUND_OPENERS = {
    1: {
        "en": (
            "You go FIRST in Round 1. Scholars have not spoken yet.\n"
            "Structure your opening in exactly these sections:\n"
            "1. **The question, in the user's own words**: quote raw_question EXACTLY, in quotes.\n"
            "2. **Academic reframing** (1-2 sentences): if one was prepared, offer it as 'For research framing, this can be read as...'. Make it clear this is an aid, NOT a replacement.\n"
            "3. **Direction menu** — one line per discipline, AND ONLY for the disciplines listed under 'Disciplines present in THIS debate'. Give 2-3 angles each. Do NOT introduce disciplines outside that list. Say explicitly: 'These are options, not assignments.'\n"
            "4. **Closing frame**: 'You are co-building a runnable spec, not debating. Connect where you can, flag fundamental disagreements where you can't. The goal is a spec the user can fork into the experiment board.'\n"
            "Do NOT answer the question yourself. Do NOT pick who should answer what. ~250 words max."
        ),
        "zh": (
            "你在第 1 轮**第一个**发言。学者们还没说话。\n"
            "开场必须分成这几段：\n"
            "1. **用户的原话**：把 raw_question 原封不动、加引号念一遍。\n"
            "2. **学术化改写**（1-2 句）：如果已经准备好了，用「从研究框架来看，这也可以被读作：……」引出。明确说清这只是辅助，**不替代原问题**。\n"
            "3. **方向菜单**——每个学科一行，**且只能列 system prompt 里「本场在场学科」那一节中的学科**，每个给 2-3 个角度。**严禁引入该列表外的学科名**。明确写「这些是选项，不是任务派单。」\n"
            "4. **定调结束语**：「各位是在**共建**一份可跑的 spec，不是在辩论。能接的接起来，接不上的**根本分歧**标出来。目标是让用户能把这份 spec 叉进实验板块去跑。」\n"
            "**不要替学者回答问题**，**不要指定谁答什么**。全文 ~250 字以内。"
        ),
    },
    "default": {
        "en": (
            "Close this round. Structure output in FOUR layers (keep them separate):\n"
            "- **Question map**: what the group now agrees the question contains.\n"
            "- **Composable paths**: where Discipline A's variable/assumption plugs into Discipline B's. Be concrete: who plugs into whom.\n"
            "- **Hypotheses to verify**: disagreements that can be resolved with evidence — who disagrees, about what, what would settle it.\n"
            "- **Irreducible disagreements**: any fundamental disagreements scholars EXPLICITLY flagged this round. Quote who and what. **Do NOT force-synthesize these into composable paths.**\n"
            "End with one line on what the next round should push further — invitation, not assignment."
        ),
        "zh": (
            "为本轮收尾。按**四层**组织，保持分开：\n"
            "- **问题地图**：讨论组现在共识的「这个问题包含什么」。\n"
            "- **可合成路径**：A 学科的变量 / 假设接到 B 学科的哪里。要具体：谁接谁。\n"
            "- **待验证假设**：能用证据解决的分歧——谁和谁分歧，分歧点是什么，什么证据能定案。\n"
            "- **根本分歧**：本轮学者**明确标过**的不能合成的根本分歧。引原话：谁说的、关于什么。**绝不要把这些强行合成进可合成路径**。\n"
            "最后用一句话说下一轮可以往哪个方向推——邀请语气，不是派活。"
        ),
    },
}

MODERATOR_ROUND_OPENERS = {
    1: {
        "en": (
            "You go FIRST in Round 1. Scholars have not spoken yet.\n"
            "Structure your opening in exactly these sections:\n"
            "1. **The question, in the user's own words**: quote the raw_question block given to you EXACTLY, in quotes. Do not paraphrase, do not academicize away their voice.\n"
            "2. **Academic reframing** (1-2 sentences): if an academic rephrasing was prepared, state it as 'For research framing, this can be read as: ...'. Make it clear this is an aid, NOT a replacement — the raw question stands.\n"
            "3. **Direction menu** — one line per discipline, AND ONLY for the disciplines listed under 'Disciplines present in THIS debate' in your system prompt. Give 2-3 angles each. **Do NOT introduce any discipline name outside that list** (no 'Physics', 'Philosophy', 'Economics' etc. unless they are literally in that list). Explicitly say 'These are options, not assignments — pick what fits you.'\n"
            "4. **One closing line** protecting freedom: 'Be bold, be speculative, cross lines — but stay welded to what the user actually asked.'\n"
            "Do NOT answer the question yourself. Do NOT pick who should answer what. ~250 words max."
        ),
        "zh": (
            "你在第 1 轮**第一个**发言。学者们还没说话。\n"
            "开场必须分成这几段：\n"
            "1. **用户的原话**：把给你的 raw_question 原封不动、加引号念一遍。**不要改写，不要学术化掉用户的语气**。\n"
            "2. **学术化改写**（1-2 句）：如果已经准备好了学术化版本，用「从研究框架来看，这也可以被读作：……」引出。明确说清这只是辅助理解，**不替代原问题**。\n"
            "3. **方向菜单**——每个学科一行，**且只能列 system prompt 里「本场在场学科」那一节中的学科**，每个给 2-3 个角度。**严禁引入该列表外的任何学科名**（用户没选的「物理学」「哲学」「经济学」这类大学科名**一律不准出现**）。明确写「这些是选项，不是任务派单——各位挑自己想切的。」\n"
            "4. **保护自由的结束语**：「大胆、思辨、可以跨学科——但要死死咬住用户真正问的那件事。」\n"
            "**不要替学者回答问题**，**不要指定谁答什么**。全文 ~250 字以内。"
        ),
    },
    # Phase 2.5 (2026-04-28): R2 收尾加"最小模型表"软提示。下一轮 (R3) 要逼到可裁决结构，
    # 但 R2 这里只是软提示，不强制方向，给 agent 一轮调整空间。R1 不动以保留探索空间。
    2: {
        "en": (
            "Close Round 2. In 3-5 bullets:\n"
            "- Who actually answered the user's raw question this round; who is still circling their discipline's comfort zone.\n"
            "- The single most unexpected or imaginative move worth amplifying next round.\n"
            "- **Soft cue for Round 3**: invite scholars to start converging toward a minimal-runnable model — what state variables, observables, control variables, termination paths, and failure conditions does each discipline contribute? Phrase as invitation, NOT assignment, and do not enumerate the field names; just point the direction.\n"
            "Terse. No recap of everything said."
        ),
        "zh": (
            "为第 2 轮收尾。3-5 条要点：\n"
            "- 本轮谁真在回答用户的原问题，谁还在绕本学科的舒适区。\n"
            "- 本轮**最出人意料或最有想象力**的一步，值得下轮放大的。\n"
            "- **给第 3 轮的软提示**：邀请学者开始向「最小可跑模型」收束——每个学科贡献哪些状态变量、可观测量、控制变量、终止路径、失效条件？用邀请的语气，不是派活，也不要把字段名一个个写死，只指方向。\n"
            "精简。不要把所有人说过的复述一遍。"
        ),
    },
    "default": {
        "en": (
            "Close this round. In 3-5 bullets:\n"
            "- Who actually answered the user's raw question this round; who drifted into their own discipline's comfort zone.\n"
            "- The single most unexpected or imaginative move worth amplifying next round.\n"
            "- One-line directive: what the NEXT round should focus on — phrased as an invitation, not an assignment.\n"
            "Terse. No recap of everything said."
        ),
        "zh": (
            "为本轮收尾。3-5 条要点：\n"
            "- 本轮谁真在回答用户的原问题，谁绕回了本学科的舒适区。\n"
            "- 本轮**最出人意料或最有想象力**的一步，值得下轮放大的。\n"
            "- 一句话：下一轮应该聚焦什么——用邀请的语气，不是派活。\n"
            "精简。不要把所有人说过的复述一遍。"
        ),
    },
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
    raw_question: str | None = None,
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
        core_hint = "你的学科是本次讨论的**核心方向**。" if weight >= 40 else "你的学科提供**辅助视角**。"
        persona_desc = persona.get("desc_zh", persona.get("desc", ""))
        # Phase 1 (2026-04-24): 按 mode 分叉使命段。
        # - debate = 破坏性检验（波普尔式）：对手/参战/筛掉坏框架
        # - free   = 建设性综合（库恩式）：共同推演/拼起来变成能跑的机器/保留根本分歧
        # 依据: notes/design.md #axl-debate-mode-design
        if mode == "debate":
            parts = [
                f"你是{rank_info['zh']}，专攻 **{discipline_name}**，参与一场跨学科学术辩论。",
                f"参与辩论的学科有：{topic}。",
                f"\n## 你的使命\n你代表 **{discipline_name}** 参战。你的对手是来自 **{others_str}** 的学者。",
                f"你需要证明你的学科视角对这个问题不可或缺，同时直接质疑其他学科的局限性。",
                f"\n## 学术定位\n{core_hint}",
            ]
        else:
            parts = [
                f"你是{rank_info['zh']}，专攻 **{discipline_name}**，和其他学科的学者一起推演用户的问题。",
                f"参与讨论的学科有：{topic}。",
                f"\n## 你的使命\n你代表 **{discipline_name}**，和来自 **{others_str}** 的学者**共同**把用户的问题推深。"
                f"你的学科在这个问题上能贡献什么、看不到什么、在哪里会失效，都要诚实说出来。"
                f"\n不是要证明你的学科最重要，而是让用户拿到一份能跑的推演 spec——"
                f"能接的假设接上去，接不上去的根本分歧**必须标出来**而不是为了协作强行糊过去。",
                f"\n## 学术定位\n{core_hint}",
            ]
        raw_for_agent = (raw_question or "").strip() or None
        prop_differs = raw_for_agent and proposition and raw_for_agent != proposition
        if raw_for_agent:
            parts.append(
                f'\n## 用户的原问题（必须紧咬）\n'
                f'用户原话如下，这是你们所有讨论的**落脚点**：\n\n'
                f'> {raw_for_agent}\n\n'
                f'即便主持人或其他人给出了学术化改写，**你的每一轮发言都必须回到这句原话本身**。'
                f'不要把它替换成学科内的另一个问题，也不要只回答改写版而不回答原话。'
            )
            if prop_differs and mode == "debate":
                parts.append(f'\n## 学术化改写（辅助理解，不替代原问题）\n"{proposition}"')
            elif prop_differs:
                parts.append(
                    f'\n## 学术化改写（辅助理解，不替代原问题）\n'
                    f'**"{proposition}"**\n'
                    f'用它帮助你组织学科论述，但回答的**对象**仍然是上面的原问题。'
                )
        elif proposition:
            if mode == "debate":
                parts.append(f'\n## 命题\n"{proposition}"')
            else:
                parts.append(
                    f'\n## 核心问题\n本次讨论要解决的核心问题是：**"{proposition}"**\n'
                    f"你的所有发言都必须围绕这个问题展开。从 **{discipline_name}** 的角度出发，"
                    f"提供其他学科无法提供的方法论、关键变量、分析框架或可操作的建议。"
                )
        if teammate_name:
            # Phase 1 (2026-04-24): teammate 定位在两种 mode 下都保留"不同流派"
            # 分化（防 P0 雷同），但 free 下软化措辞：去对抗感、去"浪费轮次"等张力词。
            if mode == "debate":
                if is_senior:
                    parts.append(
                        f"\n## 同学科队友（不同流派，不是应声筒）\n"
                        f"**{teammate_name}** 也在 {discipline_name} 内，但**流派不同**——你偏主干理论与路径定义，Ta 偏实证、案例、边界、失效条件。\n"
                        f"你们共同捍卫学科的贡献价值，**但各自从不同侧面切入**。把 Ta 看作同学科里的对照组而不是复读机——如果你们说了同一件事，就浪费了一位学者的轮次。"
                    )
                else:
                    parts.append(
                        f"\n## 同学科队友（不同流派，不是应声筒）\n"
                        f"**{teammate_name}** 是同学科的资深教授，负责主干理论与路径定义。你作为 {discipline_name} 的另一个声音，**负责实证 / 案例 / 边界 / 失效条件 / 反例**这一面——不是润色 Ta 的说法，也不是把 Ta 的主张换个措辞再念一遍。\n"
                        f"你进场时会看到 Ta 的三列摘要（已覆盖点 / 被攻击点 / 待补点），**你的主战场是「待补点」和「被攻击点」**。如果你们说的是同一件事，就浪费了一位学者的轮次。"
                    )
            else:  # free mode: 协作基调，保留分工但去张力
                if is_senior:
                    parts.append(
                        f"\n## 同学科队友（不同分工）\n"
                        f"**{teammate_name}** 和你一样在 {discipline_name} 内，你们**分工不同**——你偏主干理论与路径定义，Ta 偏实证、案例、边界、失效条件。\n"
                        f"你们从不同侧面贡献这份共建 spec。每人交出自己最擅长的那块，拼出来就是 {discipline_name} 在这份 spec 里的完整贡献。"
                    )
                else:
                    parts.append(
                        f"\n## 同学科队友（不同分工）\n"
                        f"**{teammate_name}** 是同学科的资深教授，在这份共建 spec 里贡献主干理论和路径定义。你作为 {discipline_name} 的另一个声音，贡献**实证 / 案例 / 边界 / 失效条件 / 反例**这一面。\n"
                        f"你会看到 Ta 的三列摘要（已覆盖 / 被其他学科挑战 / 待补）——你自然展开你的那块，两块拼在一起就是 {discipline_name} 的完整贡献。"
                    )
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
        core_hint = "Your discipline is a **core direction** in this discussion." if weight >= 40 else "Your discipline provides a **supporting perspective**."
        persona_desc = persona.get("desc_en", persona.get("desc", ""))
        # Phase 1 (2026-04-24): mission diverges by mode.
        # - debate = destructive test (Popper): opponents / prove indispensable / filter bad frames
        # - free   = constructive synthesis (Kuhn): co-build / produce a runnable spec / keep irreducible disagreements
        # Source: notes/design.md #axl-debate-mode-design
        if mode == "debate":
            parts = [
                f"You are a {rank_info['en']} specializing in **{discipline_name}**, in an interdisciplinary academic debate.",
                f"Disciplines in this debate: {topic}.",
                f"\n## Your Mission\nYou represent **{discipline_name}**. Your opponents are scholars from **{others_str_en}**.",
                f"Prove that YOUR discipline's perspective is indispensable for this topic, while directly challenging the limitations of other disciplines.",
                f"\n## Standing\n{core_hint}",
            ]
        else:
            parts = [
                f"You are a {rank_info['en']} specializing in **{discipline_name}**, working with scholars from other disciplines to push the user's question deeper.",
                f"Disciplines in this discussion: {topic}.",
                f"\n## Your Mission\nYou represent **{discipline_name}**, co-building a deeper understanding with scholars from **{others_str_en}**. "
                f"Be honest about what your discipline can contribute, what it cannot see, and where it breaks down.\n"
                f"The goal is NOT to prove your discipline is the most important. The goal is to hand the user a runnable simulation spec — "
                f"assumptions that can plug in, plug in; **fundamental disagreements must be flagged**, not glossed over for the sake of collaboration.",
                f"\n## Standing\n{core_hint}",
            ]
        raw_for_agent = (raw_question or "").strip() or None
        prop_differs = raw_for_agent and proposition and raw_for_agent != proposition
        if raw_for_agent:
            parts.append(
                f'\n## The user\'s raw question (stay welded to this)\n'
                f'This is the user\'s own words — the anchor for everything you say:\n\n'
                f'> {raw_for_agent}\n\n'
                f'Even if the Moderator or others provide an academic rephrasing, '
                f'**every turn you take must return to this original question itself**. '
                f'Do not substitute a different intra-disciplinary question; do not answer only the rephrasing while ignoring the raw form.'
            )
            if prop_differs and mode == "debate":
                parts.append(f'\n## Academic reframing (aid, not replacement)\n"{proposition}"')
            elif prop_differs:
                parts.append(
                    f'\n## Academic reframing (aid, not replacement)\n'
                    f'**"{proposition}"**\n'
                    f'Use it to organize your disciplinary arguments, but the target of your answer is the raw question above.'
                )
        elif proposition:
            if mode == "debate":
                parts.append(f'\n## Proposition\n"{proposition}"')
            else:
                parts.append(
                    f'\n## Core Question\nThe central question of this discussion is: **"{proposition}"**\n'
                    f"ALL your contributions must directly address this question. From **{discipline_name}**'s perspective, "
                    f"provide methodologies, variables, frameworks, or insights that OTHER disciplines cannot offer."
                )
        if teammate_name:
            # Phase 1 (2026-04-24): teammate role keeps the "different school" split
            # in both modes (prevents P0 twin collapse), but free mode uses a collaborative
            # tone rather than the debate-mode tension wording.
            if mode == "debate":
                if is_senior:
                    parts.append(
                        f"\n## Same-discipline teammate (different school of thought, not an echo)\n"
                        f"**{teammate_name}** is also in {discipline_name}, but takes a **different school**: "
                        f"you lean toward main-line theory and path definition; they lean toward "
                        f"empirics, cases, boundary conditions, failure modes. "
                        f"You co-defend the discipline's contribution but **from different angles**. "
                        f"Treat them as a within-discipline counterpart, not a parrot — if you say the "
                        f"same thing, one scholar's turn is wasted."
                    )
                else:
                    parts.append(
                        f"\n## Same-discipline teammate (different school of thought, not an echo)\n"
                        f"**{teammate_name}** is the senior Professor handling main-line theory and path definition. "
                        f"You are the other voice in {discipline_name}, responsible for "
                        f"**empirics / cases / boundary / failure modes / counter-examples** — "
                        f"NOT for polishing their claims or rephrasing their points. "
                        f"You'll see a 3-column digest of their speech (covered / attacked / gaps); "
                        f"**your battlefield is \"gaps\" and \"attacked\"**. "
                        f"If you say the same thing, one scholar's turn is wasted."
                    )
            else:  # free mode
                if is_senior:
                    parts.append(
                        f"\n## Same-discipline teammate (different role in the co-build)\n"
                        f"**{teammate_name}** is also in {discipline_name}; you two play **different roles**: "
                        f"you handle main-line theory and path definition, they handle empirics, cases, boundary, failure modes. "
                        f"You each contribute your piece to this shared spec. Put the two pieces together and you have {discipline_name}'s full contribution."
                    )
                else:
                    parts.append(
                        f"\n## Same-discipline teammate (different role in the co-build)\n"
                        f"**{teammate_name}** is the senior Professor; in this co-build spec they contribute main-line theory and path definition. "
                        f"You are the other voice in {discipline_name}, contributing **empirics / cases / boundary / failure modes / counter-examples**. "
                        f"You'll see a 3-column digest of their speech (covered / challenged / gaps) — build out your part naturally; together it's {discipline_name}'s full contribution."
                    )
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
    raw_question: str | None = None,
    suggested_dimensions: list[dict] | None = None,
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
                raw_question=raw_question,
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

    moderator_stance = "moderator" if mode == "debate" else "coordinator"
    mod_name = "主持人 (跨学科综合)" if lang == "zh" else "Moderator (Interdisciplinary)"
    # Phase 1 (2026-04-24): moderator system prompt diverges by mode.
    # debate → Director (pressure test, rank "most imaginative", name who drifted)
    # free   → Coordinator (organize into 4 layers incl. irreducible disagreements, no ranking)
    # Source: notes/design.md #axl-debate-mode-design
    if mode == "free":
        mod_prompt = FREE_MODERATOR_PROMPTS.get(lang, FREE_MODERATOR_PROMPTS["en"])
    else:
        mod_prompt = MODERATOR_PROMPTS.get(lang, MODERATOR_PROMPTS["en"])

    raw_q_clean = (raw_question or "").strip()

    present_disc_lines_zh = "\n".join(f"- {n}" for n in names_display)
    present_disc_lines_en = "\n".join(f"- {n}" for n in names_en)
    if lang == "zh":
        present_block = (
            f"\n\n## 本场在场学科（硬约束）\n"
            f"本场辩论的学者来自、且仅来自以下 {len(names_display)} 个学科：\n"
            f"{present_disc_lines_zh}\n\n"
            f"**硬性规则（违反将破坏整场辩论）**：\n"
            f"1. 方向菜单里的每一项**必须且只能**对应上述学科之一，不准引入任何其他学科名（不许出现「物理学」「政治学」「哲学」这种用户没选的大学科名）。\n"
            f"2. 方向菜单不是「这个问题可能相关的学科」，而是「**在场这几位学者的学科，各自能切什么角度**」。\n"
            f"3. 如果上述学科是 niche 子学科，就用子学科名，不准擅自把它泛化成一级学科。"
        )
    else:
        present_block = (
            f"\n\n## Disciplines present in THIS debate (hard constraint)\n"
            f"The scholars in this debate come from, and ONLY from, these {len(names_en)} disciplines:\n"
            f"{present_disc_lines_en}\n\n"
            f"**Hard rules (violating these breaks the debate)**:\n"
            f"1. Every item in the direction menu MUST correspond to one of the disciplines listed above. Do NOT introduce any other discipline name (no \"Physics\", \"Philosophy\", etc. if the user didn't pick them).\n"
            f"2. The direction menu is NOT \"disciplines that might relate to this question\" — it is \"what angles the scholars present here could attack from THEIR disciplines\".\n"
            f"3. If a listed discipline is a niche sub-field, use the sub-field name. Do NOT generalize it into a parent umbrella discipline."
        )
    mod_prompt += present_block

    def _format_dims(dims: list[dict] | None) -> str:
        if not dims:
            return ""
        lines = []
        for item in dims:
            disc = item.get("discipline") if isinstance(item, dict) else None
            angles = item.get("angles") if isinstance(item, dict) else None
            if not disc or not angles:
                continue
            angle_str = "; ".join(str(a) for a in angles)
            lines.append(f"- {disc}: {angle_str}")
        return "\n".join(lines)

    dims_block = _format_dims(suggested_dimensions)

    if raw_q_clean:
        prop_block = ""
        if proposition and proposition.strip() != raw_q_clean:
            prop_block = (
                f'\n\n学术化改写（辅助理解，**不替代**原问题）：\n**"{proposition}"**'
                if lang == "zh"
                else f'\n\nAcademic reframing (aid, not a replacement):\n**"{proposition}"**'
            )
        if lang == "zh":
            dims_section = (
                f"\n\n已经准备好的**方向菜单**（每个学科可能切入的角度，仅供参考，学者自选）：\n{dims_block}"
                if dims_block
                else "\n\n（没有预先准备的方向菜单；第 1 轮开场请严格按照「本场在场学科」那一节逐一列出，每个学科给 2-3 个角度。不准自己额外引入学科。）"
            )
            mod_prompt += (
                f'\n\n用户的原问题（**必须原话引用，不要改写掉**）：\n"""{raw_q_clean}"""'
                f'{prop_block}'
                f'{dims_section}'
                f'\n\n每轮结束时，指出谁真在回应用户的原问题，谁绕回了本学科的舒适区；一句话说下一轮的聚焦。'
            )
        else:
            dims_section = (
                f"\n\nPrepared **direction menu** (angles each discipline may attack, for reference — scholars pick their own):\n{dims_block}"
                if dims_block
                else "\n\n(No prepared direction menu; in Round 1 list EACH discipline from the 'Disciplines present' section above, with 2-3 angles each. Do NOT introduce additional disciplines.)"
            )
            mod_prompt += (
                f'\n\nThe user\'s raw question (**quote verbatim, do NOT rewrite away**):\n"""{raw_q_clean}"""'
                f'{prop_block}'
                f'{dims_section}'
                f'\n\nAt the end of each round, state who actually answered the user\'s raw question vs. who drifted into discipline-survey mode; one line on what the next round should focus on.'
            )
    elif proposition:
        if lang == "zh":
            mod_prompt += f'\n\n本次讨论的核心问题是：**"{proposition}"**\n你的总结和引导必须围绕这个问题，**围绕上面「本场在场学科」那几位展开**——不准引入列表以外的学科。每轮结束时，明确指出各学科对核心问题的具体贡献，以及还有哪些方面尚未回答。'
        else:
            mod_prompt += f'\n\nThe core question of this discussion is: **"{proposition}"**\nYour summaries and guidance must center on this question, **and stay grounded in the disciplines listed above** — do not introduce disciplines outside that list. At the end of each round, explicitly state each discipline\'s concrete contribution to answering the question, and what aspects remain unanswered.'
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

    raw_q = (getattr(debate, "raw_question", None) or "").strip()
    prop = (debate.proposition or "").strip()
    topic = raw_q or prop or debate.title
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


async def _summarize_teammate_message(
    content: str,
    teammate_name: str,
    discipline_name: str,
    language: str = "zh",
    user_id: int | None = None,
    db: Session | None = None,
) -> str:
    """Phase 0 G (2026-04-20): compress a teammate Prof's speech into a 3-column
    digest for the Assoc in the same discipline.

    Three columns:
    - 已覆盖点 (covered): 2-4 points the Prof already made
    - 被攻击点 (attacked): anything other disciplines challenged him on
    - 待补点 (gaps): disciplinary angles he didn't touch but could

    The Assoc sees this digest INSTEAD of the full 3000+ char original, so
    the LLM can't simply echo/paraphrase. See decision-gate doc B2 option B.

    Falls back to a rule-based heading+first-line extract if the LLM call
    fails (never blocks the round).
    """
    if len(content.strip()) < 200:
        # Short enough — no point summarizing; return as-is with a marker
        return content

    if language == "zh":
        prompt = (
            f"以下是你同学科队友 {teammate_name}（专攻 {discipline_name}）本轮的完整发言。"
            f"请压缩成给同学科副教授看的三列摘要，让 Ta 清楚地知道哪些点已经被说了（不要重复），"
            f"哪些点被其他学科攻击了（可以帮队友辩护或另选路径），哪些学科角度还没覆盖到（可以由 Ta 补上）。\n\n"
            f"=== 队友原文 ===\n{content}\n=== 队友原文结束 ===\n\n"
            f"请严格按以下 JSON 格式回复，不要包含任何其他文字：\n"
            f'{{"已覆盖点": ["...", "..."], "被攻击点": ["..."], "待补点": ["...", "..."]}}\n\n'
            f"规则：\n"
            f"- 已覆盖点 2-4 条，每条 ≤ 30 字，抓主张不抓措辞\n"
            f"- 被攻击点 0-2 条（如果没有人攻击他，留空数组）\n"
            f"- 待补点 2-3 条，必须是该学科能做但队友没做的角度（实证、案例、边界、反例、失效条件等）\n"
            f"- 绝对不要把队友原话照搬进来"
        )
    else:
        prompt = (
            f"Below is the full speech from your same-discipline teammate {teammate_name} "
            f"(specializing in {discipline_name}) this round. Compress it into a 3-column "
            f"digest for the Associate Professor in the same discipline, so Ta knows "
            f"which points are already covered (don't repeat), which got attacked by other "
            f"disciplines (can defend or pivot), and which angles Ta could still contribute.\n\n"
            f"=== Teammate's original ===\n{content}\n=== End ===\n\n"
            f"Reply in STRICT JSON (no other text):\n"
            f'{{"covered": ["...", "..."], "attacked": ["..."], "gaps": ["...", "..."]}}\n\n'
            f"Rules: covered 2-4 items (≤ 30 words each, capture claims not phrasing); "
            f"attacked 0-2 items (empty array if no attacks); gaps 2-3 items that THIS "
            f"discipline could still add. Do NOT quote teammate's wording verbatim."
        )

    try:
        raw = await chat_completion(
            [{"role": "user", "content": prompt}],
            model="deepseek/deepseek-chat",
            temperature=0.2,
            max_tokens=600,
            user_id=user_id,
            db=db,
        )
        import json as _json
        start = raw.index("{")
        end = raw.rindex("}") + 1
        parsed = _json.loads(raw[start:end])

        covered = parsed.get("已覆盖点") or parsed.get("covered") or []
        attacked = parsed.get("被攻击点") or parsed.get("attacked") or []
        gaps = parsed.get("待补点") or parsed.get("gaps") or []

        attacked_items = [f"- {a}" for a in attacked] or (
            ["- （无）"] if language == "zh" else ["- (none)"]
        )
        covered_items = [f"- {c}" for c in covered]
        gaps_items = [f"- {g}" for g in gaps]
        if language == "zh":
            lines = [
                f"[同学科队友 {teammate_name} 本轮发言三列摘要 —— 不是原文，不要照抄]",
                "**已覆盖点**（队友已明确讲过，你不要重复表述）:",
                *covered_items,
                "**被攻击点**（被其他学科质疑的地方，可帮辩护或换路径）:",
                *attacked_items,
                "**待补点**（同学科能贡献但队友没覆盖的角度，你的主战场）:",
                *gaps_items,
            ]
        else:
            lines = [
                f"[Teammate {teammate_name}'s speech — digest, NOT verbatim, do NOT copy]",
                "**Covered** (teammate already made these; do NOT restate):",
                *covered_items,
                "**Attacked** (other disciplines challenged these; can defend or pivot):",
                *attacked_items,
                "**Gaps** (disciplinary angles teammate missed; YOUR territory):",
                *gaps_items,
            ]
        return "\n".join(lines)

    except Exception as exc:
        logger.warning(
            "G-summarize failed for teammate %s, falling back to heading extract: %s",
            teammate_name, exc,
        )
        # Fallback: extract headings + first line of each section
        lines = content.split("\n")
        extracted = []
        for i, line in enumerate(lines):
            s = line.strip()
            if s.startswith("#") or s.startswith("**") or s.startswith("- **"):
                extracted.append(s[:120])
                if len(extracted) >= 8:
                    break
        tag = (
            f"[同学科队友 {teammate_name} 本轮发言骨架（摘要生成失败，仅展示标题）—— 不要照抄]"
            if language == "zh"
            else f"[Teammate {teammate_name}'s speech skeleton (summary failed, headings only) — do NOT copy]"
        )
        return tag + "\n" + "\n".join(extracted)


def _order_agents_for_round(agents: list[DebateAgent], round_num: int) -> list[DebateAgent]:
    """Determine speaking order for a round.

    Round 1: Moderator FIRST (frames the question, assigns angles), then professors, then juniors.
    Round 2+: Interleaved by discipline — Prof A, Prof B, Assoc A, Assoc B, then Moderator (closes round).
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
        return moderators + professors + juniors

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
    mode = getattr(debate, "mode", "debate") or "debate"

    from app.services.session_memory import build_compressed_context
    history = await build_compressed_context(
        list(debate.messages), current_round,
        depth=depth, language=lang, user_id=user_id, db=db,
    )

    # Phase 1 (2026-04-24): select round openers by mode.
    # debate → destructive test (attack / defend / final answer)
    # free   → constructive synthesis (constructive challenge / fundamental-disagreement exit / 6-field spec)
    # Source: notes/design.md #axl-debate-mode-design
    if mode == "free":
        agent_opener_table = FREE_ROUND_OPENERS
        mod_opener_table = FREE_MODERATOR_ROUND_OPENERS
    else:
        agent_opener_table = ROUND_OPENERS
        mod_opener_table = MODERATOR_ROUND_OPENERS

    opener_map = agent_opener_table.get(current_round, DEFAULT_ROUND_OPENER)
    round_opener = opener_map.get(lang, opener_map.get("en", ""))

    moderator_opener_map = mod_opener_table.get(
        current_round, mod_opener_table["default"]
    )
    moderator_opener = moderator_opener_map.get(
        lang, moderator_opener_map.get("en", "")
    )

    if any(not a.assigned_model for a in debate.agents):
        assign_models_to_agents(list(debate.agents), db)
    model_info = {a.agent_name: a.assigned_model or "default" for a in debate.agents}
    logger.info("Debate %d round %d models: %s", debate.id, current_round, model_info)

    shared_ctx, per_agent_ctx = _retrieve_zep_contexts(debate)
    speaking_order = _order_agents_for_round(list(debate.agents), current_round)

    disc_names = [d.name_en for d in debate.disciplines]
    disc_name_to_id = {d.name_en: d.id for d in debate.disciplines}

    new_messages: list[DebateMessage] = []
    # Phase 0 G (2026-04-20): cache of summaries for same-discipline teammate
    # messages, to avoid re-summarizing if multiple agents reference the same
    # teammate within one round. Key = message_id, value = 3-column digest.
    teammate_summary_cache: dict[int, str] = {}

    for agent in speaking_order:
        is_mod = agent.persona == "moderator"

        depth_tokens = {
            "quick":    (800, 600),
            "standard": (4000, 3000),
            "deep":     (8000, 6000),
            "max":      (12000, 10000),
        }
        prof_max, assoc_max = depth_tokens.get(depth, (4000, 3000))
        max_tokens = prof_max if agent.rank == "professor" else assoc_max
        if is_mod:
            max_tokens = min(max_tokens, 1200)

        messages = [
            {"role": "system", "content": agent.system_prompt},
        ]

        knowledge_msg = _build_knowledge_message(
            shared_ctx, per_agent_ctx.get(agent.id)
        )
        if knowledge_msg:
            messages.append({"role": "user", "content": knowledge_msg})

        messages.extend(history)
        agent_opener = moderator_opener if is_mod else round_opener
        messages.append({"role": "user", "content": agent_opener})

        if new_messages:
            for nm in new_messages:
                # Phase 0 G: same-discipline teammate's full text is replaced
                # with a 3-column digest to prevent echo/copy. Other
                # disciplines' speeches stay verbatim (Assoc needs to engage
                # with cross-discipline arguments fully).
                is_same_disc_teammate = (
                    nm.agent_id != agent.id
                    and not is_mod
                    and nm.agent
                    and nm.agent.discipline_id == agent.discipline_id
                    and nm.agent.discipline_id is not None
                )
                if is_same_disc_teammate:
                    if nm.id not in teammate_summary_cache:
                        teammate_summary_cache[nm.id] = await _summarize_teammate_message(
                            content=nm.content,
                            teammate_name=_agent_label(nm, debate),
                            discipline_name=(
                                nm.agent.discipline.name_zh
                                or nm.agent.discipline.name_en
                                if nm.agent.discipline else ""
                            ),
                            language=lang,
                            user_id=user_id,
                            db=db,
                        )
                    body = teammate_summary_cache[nm.id]
                else:
                    body = f"[{_agent_label(nm, debate)}]: {nm.content}"
                messages.append({
                    "role": "assistant" if nm.agent_id == agent.id else "user",
                    "content": body,
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
    """Generate structured four-part summary from the Moderator perspective.

    Phase 2 (2026-04-27): in addition to the legacy 4-section summary, this
    function now first invokes ``final_answer_layer.generate_final_answer``
    to produce a top-level Final Answer (direct_answer / why / conditions /
    next_steps). The 4 final-answer fields are written to the debate row but
    do NOT replace any of the legacy 4 summary fields.

    Final Answer Layer is best-effort: failure logs a warning and proceeds
    with the legacy summary, leaving the 4 new columns NULL.
    """
    lang = getattr(debate, "language", "zh") or "zh"
    history = _build_history(debate.messages)

    # Phase 2: Final Answer Layer — runs BEFORE 4-section summary, independent
    # LLM call. Failure does not block summary main flow.
    try:
        from app.services.final_answer_layer import generate_final_answer
        final_answer = await generate_final_answer(debate, db, user_id=user_id)
    except Exception as exc:
        logger.warning(
            "Final Answer Layer threw unexpected exception for debate %d: %s",
            debate.id, exc,
        )
        final_answer = None
    if final_answer:
        debate.summary_direct_answer = final_answer.get("direct_answer")
        debate.summary_why = final_answer.get("why")
        debate.summary_conditions = final_answer.get("conditions")
        debate.summary_next_steps = final_answer.get("next_steps")
        db.flush()
        logger.info("Final Answer Layer landed for debate %d", debate.id)
    else:
        logger.warning(
            "Final Answer Layer not produced for debate %d; legacy 4-section summary continues",
            debate.id,
        )

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

    # Phase 1 (2026-04-24): summary moderator system prompt also diverges by mode.
    # Keep 4-section schema unchanged (zero DB migration). The coordinator
    # voice will naturally tilt free-mode summaries toward "composable paths"
    # and "irreducible disagreements" tone. Source: notes/design.md #axl-debate-mode-design.
    _sum_mode = getattr(debate, "mode", "debate") or "debate"
    if _sum_mode == "free":
        mod_prompt = FREE_MODERATOR_PROMPTS.get(lang, FREE_MODERATOR_PROMPTS["en"])
    else:
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


async def suggest_mode(
    discipline_names: list[str],
    *,
    user_question: str | None = None,
    user_id: int | None = None,
    db: Session | None = None,
) -> dict:
    """Ask the LLM which debate mode fits + per-discipline attack angles.

    IMPORTANT: This function MUST be given ``user_question`` to behave correctly.
    Before 2026-04-15 it only saw discipline names and fabricated a proposition
    unrelated to what the user actually asked — root cause of "debate drifted
    off my question" complaints. See CHANGELOG.
    """
    disc_str = ", ".join(discipline_names)
    if user_question:
        user_block = (
            f"The user's raw question (their own words, keep this EXACTLY — do not rewrite it away):\n"
            f'"""{user_question}"""\n\n'
        )
    else:
        user_block = (
            "The user has NOT provided a question yet — you must NOT fabricate one. "
            "Set suggested_proposition to null and suggested_dimensions to [].\n\n"
        )

    prompt = (
        f"{user_block}"
        f"Disciplines the user picked (use these EXACT names, do not paraphrase, do not substitute with parent-umbrella names):\n"
        f"{chr(10).join(f'  - {n}' for n in discipline_names)}\n\n"
        "Task:\n"
        "1. Decide format:\n"
        "   A) free — open-ended exploration\n"
        "   B) debate — each discipline defends its own approach to a concrete question\n"
        "2. If (and only if) the user provided a question and format is 'debate', "
        "rewrite their question into a compact, operational research framing — "
        "an ACADEMIC REPHRASING that helps disciplines attack the question, "
        "NOT a replacement (raw question is still shown to debaters).\n"
        "\n"
        "   STRICT REQUIREMENTS for the academic rephrasing (Phase 2.5 product rules):\n"
        "   - Frame as a NEUTRAL MODELING problem: \"建立...的仿真模型 / 分析...之间的关系 / "
        "build a model of... / analyze the relationship among...\".\n"
        "   - DO NOT lock in a single objective function on the user's behalf. "
        "Forms like \"maximize lifespan / evade audit / prevent X / optimize Y under Z constraint\" "
        "are PROHIBITED — they prematurely narrow the problem to one direction when the user's "
        "question typically admits multiple product-level readings (mechanism modeling / "
        "simulation / audit detection / adversarial reasoning / decision boundaries / ...).\n"
        "   - Choose the WIDEST product-level reading: enumerate the variables, mechanisms, "
        "observables, and edge conditions worth modeling, so each discipline can pick its own angle.\n"
        "   - NEUTRAL stance only. The rephrasing models a question; it never makes "
        "value judgments and never injects words like \"危险/不该/不能/禁止/不应该/dangerous/"
        "should-not/must-not/avoid/prevent\". If the user's raw question is sensitive, "
        "model it as a mechanism, do not refuse and do not editorialize.\n"
        "\n"
        "3. For each discipline LISTED ABOVE, list 2-3 concrete angles it could contribute to the user's question. "
        "Be specific and distinctive per discipline. This is a MENU, not an assignment — "
        "scholars will pick what they want. Omit entirely if no user question.\n\n"
        "HARD RULES (violating will break the debate):\n"
        "- `suggested_dimensions[].discipline` MUST be one of the EXACT names from the list above. "
        "Character-for-character match. No translation, no umbrella substitution.\n"
        "- Do NOT introduce any discipline that is not in the list (e.g. don't invent 'Physics', 'Economics', 'Philosophy' etc. "
        "unless they are literally in the list).\n"
        "- If the user picked a niche sub-field like 'Opinion Dynamics and Social Influence', use THAT string, "
        "not 'Sociology' or 'Political Science' or any generalization.\n"
        "- `suggested_dimensions` must have EXACTLY one entry per listed discipline (same count, same names).\n\n"
        "Respond with ONLY a JSON object, no prose:\n"
        '{\n'
        '  "mode": "free" | "debate",\n'
        '  "reason_en": "one sentence",\n'
        '  "reason_zh": "一句话",\n'
        '  "suggested_proposition": "neutral-modeling academic rephrasing OR null",\n'
        '  "suggested_dimensions": [\n'
        '    {"discipline": "<EXACT name from the list above>", "angles": ["angle 1", "angle 2"]},\n'
        '    ...\n'
        '  ]\n'
        '}'
    )
    raw = await chat_completion(
        [{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1200,
        user_id=user_id,
        db=db,
    )

    import json
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        parsed = json.loads(raw[start:end])
    except (ValueError, json.JSONDecodeError):
        return {
            "mode": "free",
            "reason_en": "Free discussion recommended for broad exploration.",
            "reason_zh": "推荐自由讨论以进行广泛探索。",
            "suggested_proposition": None,
            "suggested_dimensions": None,
        }

    parsed.setdefault("suggested_proposition", None)
    parsed.setdefault("suggested_dimensions", None)
    dims = parsed.get("suggested_dimensions")
    if isinstance(dims, list):
        allowed = {str(n).strip() for n in discipline_names}
        cleaned = []
        dropped = []
        for item in dims:
            if not isinstance(item, dict):
                continue
            disc = item.get("discipline")
            angles = item.get("angles")
            if not disc or not isinstance(angles, list):
                continue
            disc_str = str(disc).strip()
            if disc_str not in allowed:
                dropped.append(disc_str)
                continue
            cleaned.append({
                "discipline": disc_str,
                "angles": [str(a) for a in angles if a],
            })
        if dropped:
            logger.warning(
                "suggest_mode LLM returned %d discipline(s) outside the allowed set and were dropped: %s",
                len(dropped), dropped,
            )
        parsed["suggested_dimensions"] = cleaned or None
    else:
        parsed["suggested_dimensions"] = None

    return parsed


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
