"""KPAX v0 renderers — turn moderator's 4-section Chinese summary into
structured Response JSON for verdict / estimate / plan endpoints.

Each renderer runs **one extra LLM call** (cheap model) on the 4-section
summary, asking it to project the debate into a specific schema. This is
the "structured_extractor" step from PRD §7.2 (option B):

    generate_summary  →  four Chinese sections  →  structured_extractor  →  Response JSON

Why option B (two-step) instead of A (moderator emits KPAX JSON directly):
  The 4-section Chinese summary is also the evaluation target of
  ``pilot_judge_rubric_v0.1``. Changing the moderator output shape would
  invalidate all scored experiments. Keeping AXL's academic output stable
  and letting KPAX layer its own projection is cleaner separation of concern.

**Fallback policy** (PRD §7.2 last paragraph):
  If extraction fails or LLM output violates schema, we do NOT 500. We
  build a "semi-structured" Response by stuffing the 4-section text into
  free-text fields. UX degrades gracefully; KPAX still ships a debate
  result rather than a generic error.

**evidence_ref policy** (PRD §7.4):
  Default ``source_type="expert_opinion"``, ``source_id={expert_key}``
  (v1.3 changed from ``agent_{discipline_id}`` — see §13.3 §7.4 revision).
  ``excerpt`` ≤ 200 chars, taken from agent original wording.
  v1 will upgrade to real paper citations via evidence_resolver.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy.orm import Session

from app.services.ai_provider import chat_completion
from app.services.kpax_pipeline import ExpertLensInfo, KpaxDebateResult

logger = logging.getLogger(__name__)


class RendererError(Exception):
    """Raised only for unrecoverable conditions; schema mismatches fall back."""


# ---------- helpers ----------

def _summary_to_prompt_block(summary: dict[str, str]) -> str:
    """Stitch the 4 moderator sections into a single context block."""
    parts = []
    for key, heading in (
        ("consensus", "【共识】"),
        ("disagreements", "【分歧】"),
        ("open_questions", "【开放问题】"),
        ("directions", "【建议方向】"),
    ):
        text = (summary.get(key) or "").strip()
        if text:
            parts.append(f"{heading}\n{text}")
    return "\n\n".join(parts)


def _lens_block(lenses: list[ExpertLensInfo]) -> str:
    """Give the extractor a readable list of expert_keys + zh names so it can
    attribute ``evidence_ref.source_id`` correctly."""
    if not lenses:
        return "（本场无化身席位登记）"
    lines = ["本场出席的化身（evidence_ref.source_id 必须从下面的 expert_key 里选）："]
    for lens in lenses:
        lines.append(
            f"  - expert_key={lens.expert_key} | {lens.name_zh}（{lens.name_en}）"
        )
    return "\n".join(lines)


def _default_expert_key(lenses: list[ExpertLensInfo]) -> str:
    """Pick a stable fallback expert_key for fabricated evidence_ref fallbacks."""
    return lenses[0].expert_key if lenses else "debate_0_agent_0"


def _extract_json(raw: str) -> dict[str, Any] | None:
    """Best-effort JSON extraction; returns None on failure."""
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        return json.loads(raw[start:end])
    except (ValueError, json.JSONDecodeError) as exc:
        logger.warning("kpax_renderers: JSON extraction failed: %s", exc)
        return None


async def _extract(
    prompt: str,
    *,
    db: Session,
    max_tokens: int = 2000,
) -> dict[str, Any] | None:
    """One extractor LLM call. Returns parsed JSON or None on failure."""
    try:
        raw = await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=max_tokens,
            user_id=None,
            db=db,
        )
    except Exception as exc:
        logger.warning("kpax_renderers: extractor LLM call failed: %s", exc)
        return None
    return _extract_json(raw)


def _normalize_scores(items: list[dict[str, Any]], key: str = "score") -> None:
    """Normalize a list of score-bearing dicts in place so values sum to 1.0.

    PRD §2.1 Verdict 的 options[].score 必须总和 == 1。LLM 不一定遵守，
    所以 renderer 层兜底 normalize。
    """
    if not items:
        return
    total = sum(max(0.0, float(x.get(key, 0.0) or 0.0)) for x in items)
    if total <= 0:
        equal = round(1.0 / len(items), 3)
        for x in items:
            x[key] = equal
        remainder = round(1.0 - equal * len(items), 3)
        items[0][key] = round(items[0][key] + remainder, 3)
        return
    for x in items:
        val = max(0.0, float(x.get(key, 0.0) or 0.0))
        x[key] = round(val / total, 3)


def _ensure_evidence_ref(
    obj: dict[str, Any],
    default_expert_key: str,
    default_excerpt: str,
) -> None:
    """Backfill evidence_ref if the extractor left it missing or malformed."""
    ev = obj.get("evidence_ref")
    if not isinstance(ev, dict):
        obj["evidence_ref"] = {
            "source_type": "expert_opinion",
            "source_id": default_expert_key,
            "excerpt": default_excerpt[:200],
        }
        return
    ev.setdefault("source_type", "expert_opinion")
    ev.setdefault("source_id", default_expert_key)
    if not ev.get("excerpt"):
        ev["excerpt"] = default_excerpt[:200]
    else:
        ev["excerpt"] = str(ev["excerpt"])[:200]


# ---------- renderer: verdict ----------

_VERDICT_SCHEMA_PROMPT = """你是 KPAX 决策结构化抽取器。
将下面的 AXL 多学科辩论 4 段中文总结，投影成 verdict 决策 JSON（是否题 / 选择题）。

强约束：
1. options[] 每项对应用户提供的候选 label，顺序保持一致
2. options[].score ∈ [0, 1]，所有 score 之和 == 1（会在后处理 normalize）
3. 每个 option 的 pros / cons 必须带 evidence_ref，source_id 从候选 expert_key 里选
4. recommendation.choice 必须 ∈ options[].label
5. recommendation.confidence ∈ [0, 1]，和 score 独立
6. key_drivers / key_risks / conditions 是字符串数组，每条 ≤ 80 字
7. 只输出 JSON，不要任何解释性文字

输出 schema：
{
  "options": [
    {
      "label": "<必须同用户输入>",
      "score": 0.xx,
      "pros": [{"claim": "...", "evidence_ref": {"source_type": "expert_opinion", "source_id": "<expert_key>", "excerpt": "..."}}],
      "cons": [{"claim": "...", "evidence_ref": {...}}]
    }
  ],
  "recommendation": {
    "choice": "<options 里的一个 label>",
    "confidence": 0.xx,
    "key_drivers": ["...", "..."],
    "key_risks": ["..."],
    "conditions": ["如果 X 则推荐度升至 0.xx"]
  }
}
"""


def _verdict_fallback(
    options_labels: list[str],
    summary: dict[str, str],
    lenses: list[ExpertLensInfo],
) -> dict[str, Any]:
    """Semi-structured fallback when extractor fails."""
    default_key = _default_expert_key(lenses)
    consensus_text = (summary.get("consensus") or "辩论无明显共识").strip()
    disagree_text = (summary.get("disagreements") or "辩论无明显分歧").strip()
    directions_text = (summary.get("directions") or "").strip()

    equal = round(1.0 / len(options_labels), 3)
    remainder = round(1.0 - equal * len(options_labels), 3)
    options = []
    for i, label in enumerate(options_labels):
        score = round(equal + remainder if i == 0 else equal, 3)
        options.append({
            "label": label,
            "score": score,
            "pros": [{
                "claim": f"[降级模式] 未能结构化抽取 pros，见下方 summary：{consensus_text[:150]}",
                "evidence_ref": {
                    "source_type": "expert_opinion",
                    "source_id": default_key,
                    "excerpt": consensus_text[:200],
                },
            }],
            "cons": [{
                "claim": f"[降级模式] 未能结构化抽取 cons，见下方 summary：{disagree_text[:150]}",
                "evidence_ref": {
                    "source_type": "expert_opinion",
                    "source_id": default_key,
                    "excerpt": disagree_text[:200],
                },
            }],
        })
    return {
        "options": options,
        "recommendation": {
            "choice": options_labels[0],
            "confidence": 0.5,
            "key_drivers": ["[降级模式] 结构化抽取失败，未生成 drivers"],
            "key_risks": ["[降级模式] 结构化抽取失败，未生成 risks"],
            "conditions": [directions_text[:150]] if directions_text else [],
        },
    }


async def render_verdict(
    result: KpaxDebateResult,
    question: str,
    options_labels: list[str],
    db: Session,
) -> dict[str, Any]:
    """Project KpaxDebateResult into verdict schema (是否题 / 选择题)."""
    if len(options_labels) < 2:
        raise RendererError("bad_options: verdict requires ≥2 labels")

    prompt = (
        f"{_VERDICT_SCHEMA_PROMPT}\n\n"
        f"用户问题：{question}\n"
        f"候选选项（options 按此顺序）：{json.dumps(options_labels, ensure_ascii=False)}\n\n"
        f"{_lens_block(result.expert_lenses)}\n\n"
        f"AXL 辩论总结：\n{_summary_to_prompt_block(result.summary)}\n"
    )
    parsed = await _extract(prompt, db=db, max_tokens=2500)

    if not parsed or not isinstance(parsed.get("options"), list):
        logger.warning("kpax_renderers.verdict: falling back to semi-structured")
        return _verdict_fallback(options_labels, result.summary, result.expert_lenses)

    default_key = _default_expert_key(result.expert_lenses)
    consensus = (result.summary.get("consensus") or "").strip()

    opts = parsed["options"]
    label_to_opt = {str(o.get("label", "")): o for o in opts if isinstance(o, dict)}
    ordered_opts: list[dict[str, Any]] = []
    for label in options_labels:
        opt = label_to_opt.get(label)
        if opt is None:
            opt = {"label": label, "score": 0.0, "pros": [], "cons": []}
        opt["label"] = label
        opt.setdefault("pros", [])
        opt.setdefault("cons", [])
        for item in list(opt["pros"]) + list(opt["cons"]):
            if isinstance(item, dict):
                _ensure_evidence_ref(item, default_key, consensus)
        ordered_opts.append(opt)

    _normalize_scores(ordered_opts, key="score")

    rec = parsed.get("recommendation") or {}
    choice = rec.get("choice")
    if choice not in options_labels:
        choice = options_labels[0]
    confidence = rec.get("confidence", 0.5)
    try:
        confidence = max(0.0, min(1.0, float(confidence)))
    except (TypeError, ValueError):
        confidence = 0.5

    return {
        "options": ordered_opts,
        "recommendation": {
            "choice": choice,
            "confidence": round(confidence, 3),
            "key_drivers": [str(x)[:120] for x in (rec.get("key_drivers") or [])],
            "key_risks": [str(x)[:120] for x in (rec.get("key_risks") or [])],
            "conditions": [str(x)[:200] for x in (rec.get("conditions") or [])],
        },
    }


# ---------- renderer: estimate ----------

_ESTIMATE_SCHEMA_PROMPT = """你是 KPAX 决策结构化抽取器。
将下面的 AXL 多学科辩论 4 段中文总结，投影成 estimate 评估 JSON（概率题 / 评估题）。

强约束：
1. dimensions[] 每项对应用户提供的 dimension 名（若用户没给，就用问题本身作为单一 dimension="发生概率"）
2. 对概率题：kind="probability", score ∈ [0, 1], unit="probability"
3. 对评估题：kind="score"（或 "scalar"）, score ∈ [0, 1], unit="normalized"
4. drivers / counter_drivers 每条带 weight ∈ [0, 1] + evidence_ref
5. confidence_interval 是 [low, high] 两个数，low ≤ score ≤ high
6. overall.summary 用一句话 (≤ 150 字) 综合说明
7. 只输出 JSON

输出 schema：
{
  "dimensions": [
    {
      "name": "...",
      "kind": "probability" | "score" | "scalar",
      "score": 0.xx,
      "unit": "probability" | "normalized",
      "drivers": [{"claim": "...", "weight": 0.x, "evidence_ref": {...}}],
      "counter_drivers": [{"claim": "...", "weight": 0.x, "evidence_ref": {...}}],
      "confidence_interval": [0.xx, 0.xx]
    }
  ],
  "overall": {"summary": "...", "confidence": 0.xx}
}
"""


def _estimate_fallback(
    dim_names: list[str],
    summary: dict[str, str],
    lenses: list[ExpertLensInfo],
) -> dict[str, Any]:
    default_key = _default_expert_key(lenses)
    directions = (summary.get("directions") or "未能生成结构化估计").strip()
    dims = []
    for name in dim_names:
        is_prob = "概率" in name or "probability" in name.lower()
        dims.append({
            "name": name,
            "kind": "probability" if is_prob else "score",
            "score": 0.5,
            "unit": "probability" if is_prob else "normalized",
            "drivers": [{
                "claim": f"[降级模式] 未结构化抽取：{(summary.get('consensus') or '')[:150]}",
                "weight": 0.5,
                "evidence_ref": {
                    "source_type": "expert_opinion",
                    "source_id": default_key,
                    "excerpt": (summary.get("consensus") or "")[:200],
                },
            }],
            "counter_drivers": [{
                "claim": f"[降级模式] 未结构化抽取：{(summary.get('disagreements') or '')[:150]}",
                "weight": 0.5,
                "evidence_ref": {
                    "source_type": "expert_opinion",
                    "source_id": default_key,
                    "excerpt": (summary.get("disagreements") or "")[:200],
                },
            }],
            "confidence_interval": [0.3, 0.7],
        })
    return {
        "dimensions": dims,
        "overall": {
            "summary": f"[降级模式] {directions[:140]}",
            "confidence": 0.4,
        },
    }


async def render_estimate(
    result: KpaxDebateResult,
    question: str,
    dim_names: list[str],
    db: Session,
) -> dict[str, Any]:
    """Project KpaxDebateResult into estimate schema (概率题 / 评估题)."""
    if not dim_names:
        dim_names = ["发生概率"]

    prompt = (
        f"{_ESTIMATE_SCHEMA_PROMPT}\n\n"
        f"用户问题：{question}\n"
        f"dimension 名（保持顺序）：{json.dumps(dim_names, ensure_ascii=False)}\n\n"
        f"{_lens_block(result.expert_lenses)}\n\n"
        f"AXL 辩论总结：\n{_summary_to_prompt_block(result.summary)}\n"
    )
    parsed = await _extract(prompt, db=db, max_tokens=2500)

    if not parsed or not isinstance(parsed.get("dimensions"), list):
        logger.warning("kpax_renderers.estimate: falling back to semi-structured")
        return _estimate_fallback(dim_names, result.summary, result.expert_lenses)

    default_key = _default_expert_key(result.expert_lenses)
    consensus = (result.summary.get("consensus") or "").strip()

    dims_in = parsed["dimensions"]
    name_to_dim = {str(d.get("name", "")): d for d in dims_in if isinstance(d, dict)}
    ordered_dims: list[dict[str, Any]] = []
    for name in dim_names:
        d = name_to_dim.get(name)
        if d is None:
            d = {
                "name": name,
                "kind": "score",
                "score": 0.5,
                "unit": "normalized",
                "drivers": [],
                "counter_drivers": [],
                "confidence_interval": [0.3, 0.7],
            }
        d["name"] = name

        try:
            score = max(0.0, min(1.0, float(d.get("score", 0.5))))
        except (TypeError, ValueError):
            score = 0.5
        d["score"] = round(score, 3)

        kind = d.get("kind") or "score"
        if kind not in ("probability", "score", "scalar"):
            kind = "score"
        d["kind"] = kind
        d.setdefault("unit", "probability" if kind == "probability" else "normalized")

        ci = d.get("confidence_interval")
        if (not isinstance(ci, (list, tuple)) or len(ci) != 2):
            ci = [max(0.0, score - 0.15), min(1.0, score + 0.15)]
        try:
            lo, hi = float(ci[0]), float(ci[1])
            if lo > hi:
                lo, hi = hi, lo
            d["confidence_interval"] = [round(max(0.0, lo), 3), round(min(1.0, hi), 3)]
        except (TypeError, ValueError):
            d["confidence_interval"] = [round(max(0.0, score - 0.15), 3),
                                        round(min(1.0, score + 0.15), 3)]

        for bucket in ("drivers", "counter_drivers"):
            items = d.get(bucket) or []
            if not isinstance(items, list):
                items = []
            for item in items:
                if isinstance(item, dict):
                    _ensure_evidence_ref(item, default_key, consensus)
                    try:
                        w = max(0.0, min(1.0, float(item.get("weight", 0.5))))
                    except (TypeError, ValueError):
                        w = 0.5
                    item["weight"] = round(w, 3)
            d[bucket] = [x for x in items if isinstance(x, dict)]

        ordered_dims.append(d)

    overall = parsed.get("overall") or {}
    summary_text = str(overall.get("summary") or "")[:200]
    try:
        oc = max(0.0, min(1.0, float(overall.get("confidence", 0.5))))
    except (TypeError, ValueError):
        oc = 0.5
    return {
        "dimensions": ordered_dims,
        "overall": {
            "summary": summary_text or (result.summary.get("directions") or "")[:200],
            "confidence": round(oc, 3),
        },
    }


# ---------- renderer: plan ----------

_PLAN_SCHEMA_PROMPT = """你是 KPAX 决策结构化抽取器。
将下面的 AXL 多学科辩论 4 段中文总结，投影成 plan 策略 JSON（策略题 / 路线图）。

强约束：
1. phases[] 3-5 个阶段，按时间顺序 idx=1..N
2. 每个 phase 必须带 duration (start_month / end_month / text)、actions、gate、risks
3. 每个 action 可选 evidence_ref；risk 必须带 mitigation + severity ∈ {low, medium, high, critical}
4. critical_path 是字符串数组，指向 "phaseI.actionJ" 形式的 id
5. overall_risks 是 debate 辨识的跨阶段风险
6. 只输出 JSON

输出 schema：
{
  "phases": [
    {
      "idx": 1,
      "name": "...",
      "duration": {"start_month": 0, "end_month": 3, "text": "0-3 month"},
      "actions": [{"action": "...", "owner": "self", "rationale": "...", "evidence_ref": {...}}],
      "gate": "达成 X 才进下一阶段",
      "risks": [{"risk": "...", "mitigation": "...", "severity": "medium"}]
    }
  ],
  "critical_path": ["phase1.action1", "phase2.action1"],
  "overall_risks": [{"risk": "...", "mitigation": "...", "severity": "high"}]
}
"""

_VALID_SEVERITY = {"low", "medium", "high", "critical"}


def _plan_fallback(
    summary: dict[str, str],
    lenses: list[ExpertLensInfo],
) -> dict[str, Any]:
    default_key = _default_expert_key(lenses)
    directions = (summary.get("directions") or "未能生成结构化策略").strip()
    consensus = (summary.get("consensus") or "").strip()
    disagree = (summary.get("disagreements") or "").strip()

    return {
        "phases": [
            {
                "idx": 1,
                "name": "[降级模式] 准备期",
                "duration": {"start_month": 0, "end_month": 3, "text": "0-3 month"},
                "actions": [{
                    "action": f"[降级模式] {directions[:120]}",
                    "owner": "self",
                    "rationale": consensus[:200] or "结构化抽取失败",
                    "evidence_ref": {
                        "source_type": "expert_opinion",
                        "source_id": default_key,
                        "excerpt": consensus[:200],
                    },
                }],
                "gate": "抽取失败，gate 无法生成",
                "risks": [{
                    "risk": disagree[:120] or "结构化抽取失败",
                    "mitigation": "见 debate summary 原文",
                    "severity": "medium",
                }],
            }
        ],
        "critical_path": ["phase1.action1"],
        "overall_risks": [{
            "risk": "[降级模式] 结构化抽取失败，总体风险见 summary 分歧段",
            "mitigation": "人工复读 summary",
            "severity": "medium",
        }],
    }


async def render_plan(
    result: KpaxDebateResult,
    question: str,
    goal: str | None,
    constraints: list[str],
    db: Session,
) -> dict[str, Any]:
    """Project KpaxDebateResult into plan schema (策略题)."""
    prompt_lines = [
        _PLAN_SCHEMA_PROMPT,
        "",
        f"用户问题：{question}",
    ]
    if goal:
        prompt_lines.append(f"用户目标：{goal}")
    if constraints:
        prompt_lines.append(f"约束条件：{json.dumps(constraints, ensure_ascii=False)}")
    prompt_lines += [
        "",
        _lens_block(result.expert_lenses),
        "",
        f"AXL 辩论总结：\n{_summary_to_prompt_block(result.summary)}",
    ]
    prompt = "\n".join(prompt_lines)
    parsed = await _extract(prompt, db=db, max_tokens=3500)

    if not parsed or not isinstance(parsed.get("phases"), list):
        logger.warning("kpax_renderers.plan: falling back to semi-structured")
        return _plan_fallback(result.summary, result.expert_lenses)

    default_key = _default_expert_key(result.expert_lenses)
    consensus = (result.summary.get("consensus") or "").strip()

    phases_in = parsed["phases"]
    phases_out: list[dict[str, Any]] = []
    for i, ph in enumerate(phases_in, 1):
        if not isinstance(ph, dict):
            continue
        ph["idx"] = int(ph.get("idx") or i)
        ph["name"] = str(ph.get("name") or f"阶段 {ph['idx']}")[:120]

        dur = ph.get("duration") or {}
        if not isinstance(dur, dict):
            dur = {}
        try:
            start_m = int(dur.get("start_month", 0))
            end_m = int(dur.get("end_month", start_m + 3))
        except (TypeError, ValueError):
            start_m, end_m = 0, 3
        if end_m < start_m:
            end_m = start_m + 1
        ph["duration"] = {
            "start_month": start_m,
            "end_month": end_m,
            "text": str(dur.get("text") or f"{start_m}-{end_m} month")[:60],
        }

        actions_in = ph.get("actions") or []
        if not isinstance(actions_in, list):
            actions_in = []
        actions_out = []
        for a in actions_in:
            if not isinstance(a, dict):
                continue
            a["action"] = str(a.get("action") or "")[:400]
            a["owner"] = str(a.get("owner") or "self")[:40]
            a["rationale"] = str(a.get("rationale") or "")[:400]
            if a.get("evidence_ref") is not None:
                _ensure_evidence_ref(a, default_key, consensus)
            actions_out.append(a)
        ph["actions"] = actions_out

        ph["gate"] = str(ph.get("gate") or "")[:400]

        risks_in = ph.get("risks") or []
        if not isinstance(risks_in, list):
            risks_in = []
        risks_out = []
        for r in risks_in:
            if not isinstance(r, dict):
                continue
            sev = str(r.get("severity") or "medium").lower()
            if sev not in _VALID_SEVERITY:
                sev = "medium"
            risks_out.append({
                "risk": str(r.get("risk") or "")[:400],
                "mitigation": str(r.get("mitigation") or "")[:400],
                "severity": sev,
            })
        ph["risks"] = risks_out

        phases_out.append(ph)

    if not phases_out:
        return _plan_fallback(result.summary, result.expert_lenses)

    critical_path = parsed.get("critical_path") or []
    if not isinstance(critical_path, list):
        critical_path = []
    critical_path = [str(x)[:80] for x in critical_path]
    if not critical_path:
        critical_path = [f"phase{phases_out[0]['idx']}.action1"]

    overall_risks_in = parsed.get("overall_risks") or []
    if not isinstance(overall_risks_in, list):
        overall_risks_in = []
    overall_risks_out = []
    for r in overall_risks_in:
        if not isinstance(r, dict):
            continue
        sev = str(r.get("severity") or "medium").lower()
        if sev not in _VALID_SEVERITY:
            sev = "medium"
        overall_risks_out.append({
            "risk": str(r.get("risk") or "")[:400],
            "mitigation": str(r.get("mitigation") or "")[:400],
            "severity": sev,
        })

    return {
        "phases": phases_out,
        "critical_path": critical_path,
        "overall_risks": overall_risks_out,
    }
