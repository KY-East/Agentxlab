"""Final Answer Layer (Phase 2, 2026-04-27).

在现有 4 段 summary 之前产出"对用户原问题的直接回答"，4 段结构：
  - direct_answer:  「能/不能/部分能/暂时不能」+ 一句限定（硬约束第一句开头主语）
  - why:            1-3 条核心理由
  - conditions:     在哪些条件下成立 / 哪些条件下失效
  - next_steps:     用户拿这个答案现在能做什么

debate vs free 共用 4 段结构，但 moderator prompt 在两种模式下不同：
  - debate: Why 必须是经过压力测试后仍站得住的论据（Round 3 状态锚定）
  - free:   Why 来自跨学科融合；Conditions 必须包含 transcript 中的 falsification_conditions

设计依据：notes/design.md §axl-debate-mode-design + Phase 2 plan。
关联：generate_summary() 在 4 段 summary 前调本模块；零 schema 风险——
失败时 logger.warning 不阻塞 summary 主流程。
"""
from __future__ import annotations

import json
import logging

from sqlalchemy.orm import Session

from app.models.debate import Debate, DebateMessage
from app.services.ai_provider import chat_completion

logger = logging.getLogger(__name__)


# 共有硬约束（写进两份 prompt 公共段）
_DIRECT_ANSWER_RULE_ZH = (
    "**硬约束**：`direct_answer` 字段第一句**必须**以「能 / 不能 / 部分能 / 暂时不能」之一作为"
    "开头主语，后面跟 1 句以内的限定补充，全段不超过 2 行。绝对禁止「在某种意义上能」「需要 X、Y、Z 才行」"
    "这种条件分支充斥的假明确——明确就是明确，模糊不要伪装成明确。"
)
_DIRECT_ANSWER_RULE_EN = (
    "**HARD RULE**: `direct_answer` field MUST start its first sentence with one of "
    "\"Yes\" / \"No\" / \"Partly\" / \"Not yet\" as the leading subject, followed by at most one "
    "qualifying clause, capped at 2 lines total. Do NOT write \"In a certain sense yes, but...\" "
    "or \"requires X, Y, Z to be true first\" — these are pseudo-clarity. Clarity means clarity; "
    "do not dress up uncertainty as a verdict."
)

# Phase 2.5 (2026-04-28): 数值依据待验证 conditional 规则。
# 不做硬性警告条——没数值就不显示。LLM 在生成时自然加。
_NUMERIC_PENDING_RULE_ZH = (
    "**条件性规则（仅在你的回答引用具体数值作为关键依据时触发）**：当 `why` / `conditions` / "
    "`next_steps` 任一字段出现具体数值（百分比 / 阈值 / AUC / 时间窗口 / 论文年份 / 样本量 等）"
    "作为关键依据时，必须在该数值出现处后缀「（待验证依据）」。例如：「在 N=200 样本下 AUC > 0.85 "
    "（待验证依据）」「Kahneman 2011 研究（待验证依据）」。**没引用具体数值时不要强加任何警告条**，"
    "保持自然——这条规则只针对辩论中未经第三方核验的具体数值。"
)
_NUMERIC_PENDING_RULE_EN = (
    "**Conditional rule (triggers ONLY when your answer cites concrete numeric evidence)**: "
    "if `why` / `conditions` / `next_steps` cites specific numbers (percentages / thresholds / "
    "AUC / time windows / paper years / sample sizes etc.) as key evidence, append "
    "\"(pending verification)\" immediately after each cited number. Example: \"AUC > 0.85 at "
    "N=200 (pending verification)\" / \"Kahneman 2011 (pending verification)\". **Do NOT add any "
    "warning when no concrete numbers are cited** — keep it natural. This rule targets "
    "non-third-party-verified numeric evidence from the debate only."
)


MODERATOR_FINAL_ANSWER_PROMPT_DEBATE = {
    "zh": (
        "你刚才主持了一场跨学科**压力测试辩论**。在产出共识/分歧/开放问题/研究方向 4 段综述之前，"
        "**先用 Final Answer Layer 4 段直接回答用户的原问题**。\n\n"
        "## 4 段结构（必须全部产出）\n\n"
        "1. **direct_answer**: 直接回答用户原问题。\n"
        "2. **why**: 1-3 条支撑这个回答的核心理由（每条一句话）。\n"
        "3. **conditions**: 这个回答在哪些条件下成立、哪些条件下失效。\n"
        "4. **next_steps**: 用户拿这个回答**现在**能做什么 / 下一步该怎么判断。\n\n"
        "## debate 模式专属指令\n\n"
        "- 你的 `direct_answer` 必须是经过这场压力测试后**仍站得住**的判断——经过各学科攻击与反驳"
        "之后没被驳倒的核心。\n"
        "- `why` 段的 1-3 条理由优先选择 **Round 3 仍在被使用、且没被反方在 Round 3 内重新质疑掉**"
        "的论据。被反驳后已经倒掉的论据**不要列**。\n"
        "- `conditions` 段必须包含**至少一条反方在辩论中提出的硬约束**——那些虽然没驳倒主答案、"
        "但限定了答案适用边界的条件。\n"
        "- `next_steps` 段给用户**拿走能用**的下一步动作（一份观察清单、一个验证实验、一个判断标准），"
        "不要给"研究方向建议"——研究方向放在下一层 4 段综述里。\n\n"
        f"{_DIRECT_ANSWER_RULE_ZH}\n\n"
        f"{_NUMERIC_PENDING_RULE_ZH}\n\n"
        "## 输出格式（严格 JSON，不要任何 markdown 代码块包裹）\n\n"
        "```\n"
        '{\n'
        '  "direct_answer": "能/不能/部分能/暂时不能开头的判断 + 1 句限定",\n'
        '  "why": "理由 1\\n理由 2\\n理由 3（可选）",\n'
        '  "conditions": "成立条件 + 失效条件（含至少一条反方硬约束）",\n'
        '  "next_steps": "用户立即可执行的下一步"\n'
        '}\n'
        "```\n\n"
        "只用中文。简练，每段 50-150 字以内。**不允许返回任何字段为空字符串或 null**。"
    ),
    "en": (
        "You just moderated an interdisciplinary **stress-test debate**. Before producing the "
        "4-section summary (consensus/disagreements/open questions/research directions), "
        "**first produce the Final Answer Layer — 4 fields directly answering the user's raw question**.\n\n"
        "## 4 fields (all required)\n\n"
        "1. **direct_answer**: Direct answer to the user's original question.\n"
        "2. **why**: 1-3 core reasons supporting the answer (one sentence each).\n"
        "3. **conditions**: When does this answer hold; when does it fail.\n"
        "4. **next_steps**: What can the user actually do **now** with this answer.\n\n"
        "## debate-mode specifics\n\n"
        "- Your `direct_answer` must be the core judgment that **survived** the stress test — "
        "the position not refuted after rounds of cross-disciplinary attack.\n"
        "- For `why`, prefer arguments that are **still in use in Round 3 and were not "
        "re-challenged out by opposing disciplines within Round 3**. Do NOT list arguments "
        "that have already collapsed under refutation.\n"
        "- `conditions` must include at least one hard constraint raised by the opposing side — "
        "constraints that didn't refute the main answer but bounded its applicability.\n"
        "- `next_steps` gives the user **directly actionable** next moves (a checklist, a "
        "validation experiment, a decision rule), NOT research directions — research goes in "
        "the next layer (the 4-section summary).\n\n"
        f"{_DIRECT_ANSWER_RULE_EN}\n\n"
        f"{_NUMERIC_PENDING_RULE_EN}\n\n"
        "## Output format (strict JSON, no markdown code fences)\n\n"
        "```\n"
        '{\n'
        '  "direct_answer": "Yes/No/Partly/Not-yet opening + 1 qualifying clause",\n'
        '  "why": "Reason 1\\nReason 2\\nReason 3 (optional)",\n'
        '  "conditions": "Holds when... / Fails when... (include at least one opposing-side constraint)",\n'
        '  "next_steps": "Immediate user-actionable next move"\n'
        '}\n'
        "```\n\n"
        "English only. Concise, 50-150 words per field. **No field may be empty or null**."
    ),
}


MODERATOR_FINAL_ANSWER_PROMPT_FREE = {
    "zh": (
        "你刚才主持了一场跨学科**共建 spec 协作推演**。在产出共识/分歧/开放问题/研究方向 4 段综述 + "
        "六字段 spec 之前，**先用 Final Answer Layer 4 段直接回答用户的原问题**。\n\n"
        "## 4 段结构（必须全部产出）\n\n"
        "1. **direct_answer**: 直接回答用户原问题。\n"
        "2. **why**: 1-3 条支撑这个回答的核心理由（每条一句话）。\n"
        "3. **conditions**: 这个回答在哪些条件下成立、哪些条件下失效。\n"
        "4. **next_steps**: 用户拿这个回答**现在**能做什么 / 下一步该怎么判断。\n\n"
        "## free 模式专属指令\n\n"
        "- 你的 `direct_answer` 来自**多学科共建后形成的可推进判断**——跨学科互补融合后的最锐利版本。\n"
        "- `why` 段的 1-3 条理由可以来自不同学科的视角融合，**标注每条来自哪个学科组合**（例如"
        "「来自 X 学科与 Y 学科的接口」）。\n"
        "- `conditions` 段**必须包含从 transcript 抽取的 falsification_conditions**——即 6 个 agent "
        "在 Round 3 输出的「证伪条件」字段聚合。如果有"根本分歧"，也写进来。\n"
        "- `next_steps` 段给用户**拿走能跑**的下一步——可以是一个 spec 测试方案、一份观察清单、"
        "一个先做哪步实验的判断。不要给"研究方向建议"。\n\n"
        f"{_DIRECT_ANSWER_RULE_ZH}\n\n"
        f"{_NUMERIC_PENDING_RULE_ZH}\n\n"
        "## 输出格式（严格 JSON，不要任何 markdown 代码块包裹）\n\n"
        "```\n"
        '{\n'
        '  "direct_answer": "能/不能/部分能/暂时不能开头的判断 + 1 句限定",\n'
        '  "why": "理由 1（来自 X 学科）\\n理由 2（来自 Y 与 Z 学科的接口）",\n'
        '  "conditions": "成立条件 + 从 transcript 抽出的 falsification_conditions 聚合 + 根本分歧",\n'
        '  "next_steps": "用户立即可跑的下一步 spec 测试或观察清单"\n'
        '}\n'
        "```\n\n"
        "只用中文。简练，每段 50-200 字以内（free 模式可比 debate 略长，因为要带学科标注）。"
        "**不允许返回任何字段为空字符串或 null**。"
    ),
    "en": (
        "You just moderated an interdisciplinary **co-building session producing a runnable spec**. "
        "Before producing the 4-section summary (consensus/disagreements/open questions/research "
        "directions) + 6-field spec, **first produce the Final Answer Layer — 4 fields directly "
        "answering the user's raw question**.\n\n"
        "## 4 fields (all required)\n\n"
        "1. **direct_answer**: Direct answer to the user's original question.\n"
        "2. **why**: 1-3 core reasons supporting the answer (one sentence each).\n"
        "3. **conditions**: When does this answer hold; when does it fail.\n"
        "4. **next_steps**: What can the user actually do **now** with this answer.\n\n"
        "## free-mode specifics\n\n"
        "- Your `direct_answer` is the actionable judgment formed AFTER multi-disciplinary "
        "co-building — the sharpest version of cross-discipline integration.\n"
        "- For `why`, reasons may come from different discipline interfaces. **Tag each reason "
        "with the discipline pair it came from** (e.g., \"from X-discipline & Y-discipline interface\").\n"
        "- `conditions` MUST include `falsification_conditions` extracted from the transcript — "
        "i.e., the \"falsification\" field from the 6 agents' Round 3 outputs, aggregated. "
        "Include any flagged \"fundamental disagreements\" as well.\n"
        "- `next_steps` gives the user a **runnable** next move — a spec test plan, an observation "
        "checklist, a decision on which experiment to run first. NOT research directions.\n\n"
        f"{_DIRECT_ANSWER_RULE_EN}\n\n"
        f"{_NUMERIC_PENDING_RULE_EN}\n\n"
        "## Output format (strict JSON, no markdown code fences)\n\n"
        "```\n"
        '{\n'
        '  "direct_answer": "Yes/No/Partly/Not-yet opening + 1 qualifying clause",\n'
        '  "why": "Reason 1 (from X-discipline)\\nReason 2 (from Y-Z interface)",\n'
        '  "conditions": "Holds when... + aggregated falsification_conditions from transcript + fundamental disagreements",\n'
        '  "next_steps": "Immediately runnable next-step (spec test / observation checklist)"\n'
        '}\n'
        "```\n\n"
        "English only. 50-200 words per field (free mode allows slightly more than debate "
        "to accommodate discipline tags). **No field may be empty or null**."
    ),
}


_REQUIRED_FIELDS = ("direct_answer", "why", "conditions", "next_steps")


def _moderator_model(debate: Debate) -> str | None:
    """Pick the moderator agent's assigned_model (or None for default)."""
    mod = next((a for a in debate.agents if a.persona == "moderator"), None)
    if mod and mod.assigned_model:
        return mod.assigned_model
    return None


def _build_history(messages: list[DebateMessage]) -> list[dict]:
    """Mirror debate_engine._build_history shape (compact role/content format)."""
    out: list[dict] = []
    for m in messages:
        if m.role == "agent" and m.agent:
            out.append({"role": "user", "content": f"[{m.agent.agent_name}]: {m.content}"})
        elif m.role == "system":
            out.append({"role": "system", "content": m.content})
        elif m.role == "user":
            out.append({"role": "user", "content": m.content})
    return out


def _parse_json_loose(raw: str) -> dict | None:
    """LLM 偶发用 ```json ... ``` 包裹或前后多塞解释，兜底从首个 { 到最后一个 } 切。"""
    if not raw:
        return None
    raw = raw.strip()
    if raw.startswith("```"):
        # 去掉 ```json / ``` 包裹
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw.lstrip("`")
        if raw.endswith("```"):
            raw = raw[: raw.rindex("```")].rstrip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        return json.loads(raw[start:end])
    except (ValueError, json.JSONDecodeError):
        return None


async def generate_final_answer(
    debate: Debate,
    db: Session,
    *,
    user_id: int | None = None,
) -> dict[str, str] | None:
    """Independent LLM call producing 4-field Final Answer Layer.

    Returns dict with keys: direct_answer / why / conditions / next_steps.
    Returns None on failure (caller should log warning and continue summary
    main flow without raising — Final Answer Layer is best-effort).
    """
    lang = getattr(debate, "language", "zh") or "zh"
    mode = getattr(debate, "mode", "debate") or "debate"

    # Pick mode-specific prompt
    if mode == "free":
        prompt_table = MODERATOR_FINAL_ANSWER_PROMPT_FREE
    else:
        prompt_table = MODERATOR_FINAL_ANSWER_PROMPT_DEBATE
    user_prompt = prompt_table.get(lang, prompt_table["en"])

    # Anchor user's raw question explicitly so LLM doesn't drift to the
    # academic rephrasing (proposition).
    raw_q = (getattr(debate, "raw_question", None) or "").strip()
    proposition = (debate.proposition or "").strip()
    if raw_q:
        if lang == "zh":
            anchor = (
                f"\n\n## 用户的原问题（必须直接回答这个，不是回答学术化改写版）\n"
                f'原话："{raw_q}"\n'
            )
            if proposition and proposition != raw_q:
                anchor += f'学术化改写（仅供辅助理解）："{proposition}"\n'
        else:
            anchor = (
                f"\n\n## User's raw question (answer THIS, not the academic rephrasing)\n"
                f'Original: "{raw_q}"\n'
            )
            if proposition and proposition != raw_q:
                anchor += f'Academic rephrasing (auxiliary only): "{proposition}"\n'
        user_prompt = user_prompt + anchor

    history = _build_history(list(debate.messages))
    messages = [
        {"role": "system", "content": user_prompt},
        *history,
        {"role": "user", "content": (
            "请按上面的 JSON 格式严格输出 Final Answer Layer 4 段。" if lang == "zh"
            else "Output the Final Answer Layer 4 fields strictly in the JSON format above."
        )},
    ]

    try:
        raw = await chat_completion(
            messages,
            model=_moderator_model(debate),
            temperature=0.4,
            max_tokens=1500,
            user_id=user_id,
            db=db,
        )
    except Exception as exc:
        logger.warning("Final Answer Layer LLM call failed for debate %d: %s", debate.id, exc)
        return None

    parsed = _parse_json_loose(raw)
    if not parsed or not isinstance(parsed, dict):
        logger.warning(
            "Final Answer Layer JSON parse failed for debate %d. Raw head: %s",
            debate.id, (raw or "")[:200],
        )
        return None

    # 4 fields all required, missing/empty → reject (Phase 2 §2.2 完整性硬约束)
    out: dict[str, str] = {}
    for k in _REQUIRED_FIELDS:
        v = parsed.get(k)
        if not isinstance(v, str) or not v.strip():
            logger.warning(
                "Final Answer Layer missing/empty field %r for debate %d", k, debate.id,
            )
            return None
        out[k] = v.strip()

    return out
