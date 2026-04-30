"""KPAX-facing HTTP API — real v0 implementation (no longer mock).

This is the **only** boundary AXL exposes to KPAX. KPAX never imports AXL
Python modules; it only talks to these endpoints over HTTP.

Spec: ``app/routers/kpax_api_spec.md`` (v1.3, 2026-04-17)

Three analyze endpoints (grouped by output structure, not by user-facing
question type):
  - POST /axl/v1/analyze/verdict    (是否题 + 选择题)
  - POST /axl/v1/analyze/estimate   (概率题 + 评估题)
  - POST /axl/v1/analyze/plan       (策略题)

Two followup endpoints (v1; v0 placeholder returns 501):
  - POST /axl/v1/debate/{debate_id}/agent/{expert_key}/ask
  - POST /axl/v1/skill/{skill_id}/ask

v1.3 Platform extensions (PRD §13):
  - expert_lenses[] every item carries ``expert_key`` + ``skill_source`` + ``name_zh``
  - ``expert_key`` regex allows both ``debate_{id}_agent_{aid}`` and ``skill_{sid}``
    (v0 only emits the first)
  - Request carries ``llm_provider_override`` (v0 must be null; non-null → 501)
  - ``wallet_address`` field on Request (optional, v0 format-loose)
  - SSE via ``stream=true`` (step 10 — currently 501 until wired)
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.kpax_pipeline import (
    DEPTH_TO_ROUNDS,
    KpaxDebateResult,
    KpaxNotImplementedV0,
    KpaxPipelineError,
    run_kpax_debate,
    stream_kpax_debate_events,
)
from app.services.kpax_renderers import (
    RendererError,
    render_estimate,
    render_plan,
    render_verdict,
)

logger = logging.getLogger(__name__)

# Analyze endpoints under /axl/v1/analyze; followup endpoints under /axl/v1.
router = APIRouter(prefix="/axl/v1/analyze", tags=["kpax"])
followup_router = APIRouter(prefix="/axl/v1", tags=["kpax-followup"])


# ---------- schemas ----------

Depth = Literal["quick", "standard", "deep"]

# v1.3: allow both debate_* and skill_* expert_key formats (PRD §13.3 §8.2)
EXPERT_KEY_PATTERN = r"^(debate_\d+_agent_\d+|skill_[a-z0-9_]+)$"

SkillSource = Literal[
    "platform_discipline",   # v0 唯一值
    "platform_skill",        # v1 平台预置 skill 化身
    "user_created",          # v2 用户自建
    "third_party_creator",   # v2 第三方上架
]


class EvidenceRef(BaseModel):
    source_type: Literal["paper", "reddit", "zhihu", "expert_opinion", "other"]
    source_id: str
    excerpt: str | None = None


class ExpertLens(BaseModel):
    """v1.3 extended: expert_key + name_zh + skill_source now required (PRD §13.3 §8.x)."""

    expert_key: str = Field(..., pattern=EXPERT_KEY_PATTERN)
    discipline_id: int
    name_en: str
    name_zh: str
    skill_source: SkillSource = "platform_discipline"


class TokenUsage(BaseModel):
    input: int
    output: int


class DebateTrace(BaseModel):
    debate_id: int
    expert_lenses: list[ExpertLens]
    rounds: int
    token_usage: TokenUsage
    cost_usd: float


class Meta(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_moderator: str = "anthropic/claude-opus-4-6"
    axl_version: str = "2.0"
    depth: Depth


# v1.3: llm_provider_override is new on every Request (PRD §13.3 §9)
class _BaseKpaxRequest(BaseModel):
    question: str = Field(..., min_length=5)
    user_context: dict[str, Any] = Field(default_factory=dict)
    depth: Depth = "standard"
    stream: bool = False

    # v0: must be null; non-null throws 501 not_implemented_in_v0 (§13.3 §9)
    llm_provider_override: dict[str, Any] | None = None

    # v1.3: wallet_address replaces user_id at the KPAX ↔ AXL boundary (§13.4).
    # v0 format is loose (any string). Empty / missing → treated as guest.
    wallet_address: str | None = None


# ----- verdict -----

class VerdictRequest(_BaseKpaxRequest):
    options: list[str] | None = None


class VerdictClaim(BaseModel):
    claim: str
    evidence_ref: EvidenceRef


class VerdictOption(BaseModel):
    label: str
    score: float  # [0, 1]; all options sum to 1 after renderer normalize
    pros: list[VerdictClaim]
    cons: list[VerdictClaim]


class VerdictRecommendation(BaseModel):
    choice: str
    confidence: float  # [0, 1], independent from score
    key_drivers: list[str]
    key_risks: list[str]
    conditions: list[str]


class VerdictResponse(BaseModel):
    question_type: Literal["verdict"] = "verdict"
    options: list[VerdictOption]
    recommendation: VerdictRecommendation
    debate_trace: DebateTrace
    meta: Meta


# ----- estimate -----

class EstimateRequest(_BaseKpaxRequest):
    dimensions: list[str] | None = None


class EstimateDriver(BaseModel):
    claim: str
    weight: float
    evidence_ref: EvidenceRef


class EstimateDimension(BaseModel):
    name: str
    kind: Literal["probability", "scalar", "score"]
    score: float
    unit: str
    drivers: list[EstimateDriver]
    counter_drivers: list[EstimateDriver]
    confidence_interval: tuple[float, float]


class EstimateOverall(BaseModel):
    summary: str
    confidence: float


class EstimateResponse(BaseModel):
    question_type: Literal["estimate"] = "estimate"
    dimensions: list[EstimateDimension]
    overall: EstimateOverall
    debate_trace: DebateTrace
    meta: Meta


# ----- plan -----

class PlanRequest(_BaseKpaxRequest):
    goal: str | None = None
    constraints: list[str] = Field(default_factory=list)

    # PRD §2.3: plan endpoint defaults to deep.
    depth: Depth = "deep"


class PhaseDuration(BaseModel):
    start_month: int
    end_month: int
    text: str


class PlanAction(BaseModel):
    action: str
    owner: str
    rationale: str
    evidence_ref: EvidenceRef | None = None


class PlanRisk(BaseModel):
    risk: str
    mitigation: str
    severity: Literal["low", "medium", "high", "critical"]


class PlanPhase(BaseModel):
    idx: int
    name: str
    duration: PhaseDuration
    actions: list[PlanAction]
    gate: str
    risks: list[PlanRisk]


class PlanResponse(BaseModel):
    question_type: Literal["plan"] = "plan"
    phases: list[PlanPhase]
    critical_path: list[str]
    overall_risks: list[PlanRisk]
    debate_trace: DebateTrace
    meta: Meta


# ---------- helpers ----------

def _reject_byom_v0(override: dict[str, Any] | None) -> None:
    """v1.3 PRD §13.3 §9: v0 must reject non-null llm_provider_override."""
    if override is None:
        return
    raise HTTPException(
        status_code=501,
        detail={
            "code": "not_implemented_in_v0",
            "feature": "llm_provider_override",
            "scheduled": "v1",
        },
    )


def _pipeline_exc_to_http(exc: Exception) -> HTTPException:
    """Map pipeline exceptions to documented HTTP errors (spec §4)."""
    msg = str(exc)
    if "debate_failed" in msg:
        return HTTPException(status_code=500, detail={"code": "debate_failed", "reason": msg})
    if "summary_failed" in msg:
        return HTTPException(status_code=500, detail={"code": "debate_failed", "reason": msg})
    return HTTPException(status_code=500, detail={"code": "debate_failed", "reason": msg})


# ---------- SSE helpers (step 10) ----------

def _sse_frame(event: str, data: dict[str, Any]) -> str:
    """Format one SSE frame. Trailing blank line separates events per the spec."""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def _sse_stream(
    event_source: AsyncIterator[tuple[str, dict[str, Any], KpaxDebateResult | None]],
    render_final_dict: Callable[[KpaxDebateResult], Awaitable[dict[str, Any]]],
) -> AsyncIterator[bytes]:
    """Consume pipeline events, run renderer on summary_ready, emit SSE bytes.

    Errors raised mid-stream become an ``error`` event + graceful close, not
    a 500. HTTP status was already 200 by the time the first byte flushed,
    so any late failure has to ride inside the SSE body.
    """
    try:
        async for event, data, result in event_source:
            if event == "summary_ready" and result is not None:
                try:
                    final_dict = await render_final_dict(result)
                    yield _sse_frame("final", final_dict).encode("utf-8")
                except Exception as exc:
                    logger.exception("kpax_router: render_final_dict failed")
                    yield _sse_frame(
                        "error",
                        {"code": "render_failed", "reason": str(exc)},
                    ).encode("utf-8")
            else:
                yield _sse_frame(event, data).encode("utf-8")
    except KpaxNotImplementedV0 as exc:
        yield _sse_frame(
            "error",
            {"code": "not_implemented_in_v0", "reason": str(exc)},
        ).encode("utf-8")
    except KpaxPipelineError as exc:
        yield _sse_frame(
            "error",
            {"code": "debate_failed", "reason": str(exc)},
        ).encode("utf-8")
    except ValueError as exc:
        yield _sse_frame(
            "error",
            {"code": "invalid_depth", "reason": str(exc)},
        ).encode("utf-8")
    except Exception as exc:
        logger.exception("kpax_router: unexpected SSE stream error")
        yield _sse_frame(
            "error",
            {"code": "internal_error", "reason": str(exc)},
        ).encode("utf-8")


_SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",  # disable nginx buffering if proxied
}


def _build_debate_trace(result, /) -> DebateTrace:
    """Convert pipeline ExpertLensInfo + cost into the wire DebateTrace."""
    return DebateTrace(
        debate_id=result.debate_id,
        expert_lenses=[
            ExpertLens(
                expert_key=lens.expert_key,
                discipline_id=lens.discipline_id,
                name_en=lens.name_en,
                name_zh=lens.name_zh,
                skill_source=lens.skill_source,  # type: ignore[arg-type]
            )
            for lens in result.expert_lenses
        ],
        rounds=result.rounds,
        token_usage=TokenUsage(
            input=result.token_usage.get("input", 0),
            output=result.token_usage.get("output", 0),
        ),
        cost_usd=result.cost_usd,
    )


# ---------- analyze endpoints (real v0) ----------

def _assemble_verdict(
    result: KpaxDebateResult,
    rendered: dict[str, Any],
    depth: Depth,
) -> VerdictResponse:
    return VerdictResponse(
        options=[VerdictOption(**o) for o in rendered["options"]],
        recommendation=VerdictRecommendation(**rendered["recommendation"]),
        debate_trace=_build_debate_trace(result),
        meta=Meta(depth=depth),
    )


@router.post("/verdict", response_model=VerdictResponse)
async def analyze_verdict(
    req: VerdictRequest,
    db: Session = Depends(get_db),
) -> VerdictResponse | StreamingResponse:
    _reject_byom_v0(req.llm_provider_override)

    options_labels = req.options or ["做", "不做"]
    if len(options_labels) < 2:
        raise HTTPException(
            status_code=400,
            detail={"code": "bad_options", "reason": "verdict requires ≥2 options"},
        )
    if req.depth not in DEPTH_TO_ROUNDS:
        raise HTTPException(
            status_code=400,
            detail={"code": "invalid_depth", "allowed": list(DEPTH_TO_ROUNDS.keys())},
        )

    if req.stream:
        async def _render_final(result: KpaxDebateResult) -> dict[str, Any]:
            rendered = await render_verdict(result, req.question, options_labels, db)
            return _assemble_verdict(result, rendered, req.depth).model_dump()

        source = stream_kpax_debate_events(
            question=req.question,
            user_context=req.user_context,
            depth=req.depth,
            db=db,
            wallet_address=req.wallet_address,
            llm_provider_override=req.llm_provider_override,
        )
        return StreamingResponse(
            _sse_stream(source, _render_final),
            media_type="text/event-stream",
            headers=_SSE_HEADERS,
        )

    try:
        result = await run_kpax_debate(
            question=req.question,
            user_context=req.user_context,
            depth=req.depth,
            db=db,
            wallet_address=req.wallet_address,
            llm_provider_override=req.llm_provider_override,
        )
    except KpaxNotImplementedV0 as exc:
        raise HTTPException(status_code=501, detail={"code": "not_implemented_in_v0", "reason": str(exc)})
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"code": "invalid_depth", "reason": str(exc)})
    except KpaxPipelineError as exc:
        raise _pipeline_exc_to_http(exc)

    try:
        rendered = await render_verdict(result, req.question, options_labels, db)
    except RendererError as exc:
        raise HTTPException(status_code=400, detail={"code": "bad_options", "reason": str(exc)})

    return _assemble_verdict(result, rendered, req.depth)


def _assemble_estimate(
    result: KpaxDebateResult,
    rendered: dict[str, Any],
    depth: Depth,
) -> EstimateResponse:
    dims: list[EstimateDimension] = []
    for d in rendered["dimensions"]:
        drivers = [EstimateDriver(**x) for x in d.get("drivers", []) if isinstance(x, dict)]
        counter = [EstimateDriver(**x) for x in d.get("counter_drivers", []) if isinstance(x, dict)]
        ci = d["confidence_interval"]
        dims.append(EstimateDimension(
            name=d["name"],
            kind=d["kind"],
            score=d["score"],
            unit=d["unit"],
            drivers=drivers,
            counter_drivers=counter,
            confidence_interval=(ci[0], ci[1]),
        ))
    return EstimateResponse(
        dimensions=dims,
        overall=EstimateOverall(**rendered["overall"]),
        debate_trace=_build_debate_trace(result),
        meta=Meta(depth=depth),
    )


@router.post("/estimate", response_model=EstimateResponse)
async def analyze_estimate(
    req: EstimateRequest,
    db: Session = Depends(get_db),
) -> EstimateResponse | StreamingResponse:
    _reject_byom_v0(req.llm_provider_override)

    if req.depth not in DEPTH_TO_ROUNDS:
        raise HTTPException(
            status_code=400,
            detail={"code": "invalid_depth", "allowed": list(DEPTH_TO_ROUNDS.keys())},
        )

    dim_names = req.dimensions or ["发生概率"]

    if req.stream:
        async def _render_final(result: KpaxDebateResult) -> dict[str, Any]:
            rendered = await render_estimate(result, req.question, dim_names, db)
            return _assemble_estimate(result, rendered, req.depth).model_dump()

        source = stream_kpax_debate_events(
            question=req.question,
            user_context=req.user_context,
            depth=req.depth,
            db=db,
            wallet_address=req.wallet_address,
            llm_provider_override=req.llm_provider_override,
        )
        return StreamingResponse(
            _sse_stream(source, _render_final),
            media_type="text/event-stream",
            headers=_SSE_HEADERS,
        )

    try:
        result = await run_kpax_debate(
            question=req.question,
            user_context=req.user_context,
            depth=req.depth,
            db=db,
            wallet_address=req.wallet_address,
            llm_provider_override=req.llm_provider_override,
        )
    except KpaxNotImplementedV0 as exc:
        raise HTTPException(status_code=501, detail={"code": "not_implemented_in_v0", "reason": str(exc)})
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"code": "invalid_depth", "reason": str(exc)})
    except KpaxPipelineError as exc:
        raise _pipeline_exc_to_http(exc)

    rendered = await render_estimate(result, req.question, dim_names, db)
    return _assemble_estimate(result, rendered, req.depth)


def _assemble_plan(
    result: KpaxDebateResult,
    rendered: dict[str, Any],
    depth: Depth,
) -> PlanResponse:
    phases: list[PlanPhase] = []
    for ph in rendered["phases"]:
        actions = []
        for a in ph["actions"]:
            ev = a.get("evidence_ref")
            actions.append(PlanAction(
                action=a["action"],
                owner=a["owner"],
                rationale=a["rationale"],
                evidence_ref=EvidenceRef(**ev) if isinstance(ev, dict) else None,
            ))
        risks = [PlanRisk(**r) for r in ph["risks"] if isinstance(r, dict)]
        phases.append(PlanPhase(
            idx=ph["idx"],
            name=ph["name"],
            duration=PhaseDuration(**ph["duration"]),
            actions=actions,
            gate=ph["gate"],
            risks=risks,
        ))
    overall_risks = [PlanRisk(**r) for r in rendered["overall_risks"] if isinstance(r, dict)]
    return PlanResponse(
        phases=phases,
        critical_path=rendered["critical_path"],
        overall_risks=overall_risks,
        debate_trace=_build_debate_trace(result),
        meta=Meta(depth=depth),
    )


@router.post("/plan", response_model=PlanResponse)
async def analyze_plan(
    req: PlanRequest,
    db: Session = Depends(get_db),
) -> PlanResponse | StreamingResponse:
    _reject_byom_v0(req.llm_provider_override)

    if req.depth not in DEPTH_TO_ROUNDS:
        raise HTTPException(
            status_code=400,
            detail={"code": "invalid_depth", "allowed": list(DEPTH_TO_ROUNDS.keys())},
        )

    if req.stream:
        async def _render_final(result: KpaxDebateResult) -> dict[str, Any]:
            rendered = await render_plan(result, req.question, req.goal, req.constraints, db)
            return _assemble_plan(result, rendered, req.depth).model_dump()

        source = stream_kpax_debate_events(
            question=req.question,
            user_context=req.user_context,
            depth=req.depth,
            db=db,
            wallet_address=req.wallet_address,
            llm_provider_override=req.llm_provider_override,
        )
        return StreamingResponse(
            _sse_stream(source, _render_final),
            media_type="text/event-stream",
            headers=_SSE_HEADERS,
        )

    try:
        result = await run_kpax_debate(
            question=req.question,
            user_context=req.user_context,
            depth=req.depth,
            db=db,
            wallet_address=req.wallet_address,
            llm_provider_override=req.llm_provider_override,
        )
    except KpaxNotImplementedV0 as exc:
        raise HTTPException(status_code=501, detail={"code": "not_implemented_in_v0", "reason": str(exc)})
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"code": "invalid_depth", "reason": str(exc)})
    except KpaxPipelineError as exc:
        raise _pipeline_exc_to_http(exc)

    rendered = await render_plan(result, req.question, req.goal, req.constraints, db)
    return _assemble_plan(result, rendered, req.depth)


# ---------- followup endpoints (v0 placeholder — always 501) ----------

@followup_router.post("/debate/{debate_id}/agent/{expert_key}/ask")
async def debate_agent_followup(debate_id: int, expert_key: str) -> None:
    """Followup on a specific agent from a finished debate.

    v1 implementation: single chat_completion reusing that agent's system_prompt +
    original debate messages. v0 returns 501 to lock the URL shape (spec §9 / §13.3).
    """
    raise HTTPException(
        status_code=501,
        detail={
            "code": "followup_not_implemented_in_v0",
            "scheduled": "v1",
            "url_locked": True,
        },
    )


@followup_router.post("/skill/{skill_id}/ask")
async def skill_followup(skill_id: str) -> None:
    """Ask a globally persistent skill avatar directly (no debate context required).

    v1 endpoint for calling a Munger / Feynman / Paul Graham skill avatar standalone.
    v0 returns 501 (spec §13.3 §9 newly added endpoint).
    """
    raise HTTPException(
        status_code=501,
        detail={
            "code": "skill_followup_not_implemented_in_v0",
            "scheduled": "v1",
            "url_locked": True,
        },
    )
