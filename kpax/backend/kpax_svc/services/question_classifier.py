"""Question classifier — route raw user input to one of the three AXL endpoints.

Spec reference: `projects/knowledge-graph/backend/app/routers/kpax_api_spec.md`
Section 1 rule 2 — AXL exposes 3 endpoints grouped by output structure:
  - verdict  — user wants a decision / choice between options
  - estimate — user wants a score / probability / evaluation
  - plan     — user wants a multi-step roadmap

The five product-level question types from KPAX.md collapse to three:
  是否题 / 选择题            → verdict
  概率题 / 评估题            → estimate
  策略题                     → plan

This module runs one LLM call to classify, and also extracts auxiliary
fields (options for verdict, dimensions for estimate, goal/constraints
for plan) so the caller can build an AXL request without a second pass.

v0 behavior: if the LLM output is unparseable, fall back to `verdict`
with auto-detected options — the most common case.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Literal

from pydantic import BaseModel

logger = logging.getLogger(__name__)

RouteKind = Literal["verdict", "estimate", "plan"]


class ClassifiedRoute(BaseModel):
    kind: RouteKind
    # verdict:
    options: list[str] | None = None
    # estimate:
    dimensions: list[str] | None = None
    # plan:
    goal: str | None = None
    constraints: list[str] | None = None
    # diagnostics
    rationale: str = ""


SYSTEM_PROMPT = """你是 KPAX 的问题路由分类器。用户会输入一个决策类问题，你要把它归到三类之一：

1. verdict — 用户要的是**做/不做 或 多选一的判断**。典型：
   - 是否题（"该不该辞职"）→ options=["做","不做"]
   - 选择题（"北京还是上海"）→ options=["北京","上海"]
   抽取每个选项的 label 放进 options 数组。

2. estimate — 用户要的是**一个或多个维度的打分/概率/估值**。典型：
   - 概率题（"巴西能拿世界杯吗"）→ dimensions=["冠军概率"]
   - 评估题（"这个 offer 怎么样"）→ dimensions=["薪酬","成长","风险"] 等多维
   抽取要评估的维度名放进 dimensions 数组。

3. plan — 用户要的是**分阶段的行动路径 / roadmap**。典型：
   - "怎么从零开始做 SaaS"
   - "怎么考上清华"
   抽取用户的目标放进 goal，外部约束放进 constraints 数组。

严格输出 JSON：
{
  "kind": "verdict" | "estimate" | "plan",
  "options": [ ... ]          // verdict 必填，其他填 null
  "dimensions": [ ... ]       // estimate 必填，其他填 null
  "goal": "..."               // plan 必填，其他填 null
  "constraints": [ ... ]      // plan 可选，其他填 null
  "rationale": "一句话说明为什么归到这一类"
}

判断优先级：
- 如果同时像 verdict 和 plan（"该不该创业，怎么做"），优先归 plan
- 如果同时像 estimate 和 verdict（"这个 offer 值不值得接"），优先归 verdict，options=["接","不接"]
- 无法判断时默认 verdict，options=["做","不做"]
"""


async def classify(question: str, chat_fn: Any) -> ClassifiedRoute:
    """Classify a user question into one of the three AXL routes.

    `chat_fn` is an async function `(messages, temperature, max_tokens) -> str`.
    Injected so this module has zero AXL import dependency — the caller
    passes in whichever LLM provider KPAX uses.
    """
    raw = await chat_fn(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        temperature=0.0,
        max_tokens=800,
    )

    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        parsed = json.loads(raw[start:end])
    except (ValueError, json.JSONDecodeError) as exc:
        logger.warning("classifier LLM output unparseable: %s\n%s", exc, raw)
        return _fallback(question)

    kind = parsed.get("kind")
    if kind not in ("verdict", "estimate", "plan"):
        logger.warning("classifier returned invalid kind: %r", kind)
        return _fallback(question)

    return ClassifiedRoute(
        kind=kind,
        options=parsed.get("options"),
        dimensions=parsed.get("dimensions"),
        goal=parsed.get("goal"),
        constraints=parsed.get("constraints"),
        rationale=parsed.get("rationale", ""),
    )


def _fallback(question: str) -> ClassifiedRoute:
    return ClassifiedRoute(
        kind="verdict",
        options=["做", "不做"],
        rationale="fallback: LLM classifier output unparseable",
    )
