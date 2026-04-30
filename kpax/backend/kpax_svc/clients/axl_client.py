"""AXL HTTP client.

KPAX's only bridge to Agent X Lab. Wraps the three analyze endpoints
defined in `projects/knowledge-graph/backend/app/routers/kpax_api_spec.md` v1.1.

Design rules (from Ken 2026-04-15 hard rule #6):
- KPAX never imports AXL Python modules
- Pydantic models are mirrored here, not shared with AXL
- HTTP only — localhost in dev, cross-machine in prod
- Base URL from env `AXL_BASE_URL`, defaults to `http://localhost:8000`

v0: stream=false only. SSE wiring in v0.1.
"""

from __future__ import annotations

import os
from typing import Any, Literal

import httpx
from pydantic import BaseModel, Field

Depth = Literal["quick", "standard", "deep"]


# ── mirrored schemas (DO NOT import from AXL) ──────────────────────

class EvidenceRef(BaseModel):
    source_type: Literal["paper", "reddit", "zhihu", "expert_opinion", "other"]
    source_id: str
    excerpt: str | None = None


class ExpertLens(BaseModel):
    discipline_id: int
    name_en: str


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
    model_moderator: str
    axl_version: str
    depth: Depth


# verdict ---------------------------------------------------------

class VerdictClaim(BaseModel):
    claim: str
    evidence_ref: EvidenceRef


class VerdictOption(BaseModel):
    label: str
    score: float
    pros: list[VerdictClaim]
    cons: list[VerdictClaim]


class VerdictRecommendation(BaseModel):
    choice: str
    confidence: float
    key_drivers: list[str]
    key_risks: list[str]
    conditions: list[str]


class VerdictResponse(BaseModel):
    question_type: Literal["verdict"]
    options: list[VerdictOption]
    recommendation: VerdictRecommendation
    debate_trace: DebateTrace
    meta: Meta


# estimate --------------------------------------------------------

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
    question_type: Literal["estimate"]
    dimensions: list[EstimateDimension]
    overall: EstimateOverall
    debate_trace: DebateTrace
    meta: Meta


# plan ------------------------------------------------------------

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
    question_type: Literal["plan"]
    phases: list[PlanPhase]
    critical_path: list[str]
    overall_risks: list[PlanRisk]
    debate_trace: DebateTrace
    meta: Meta


# ── client ─────────────────────────────────────────────────────────

class AXLClient:
    """Thin async httpx wrapper around AXL /axl/v1/analyze/*.

    One instance per request is fine (no connection pooling across KPAX
    handlers yet). Timeouts are generous because debate can take minutes.
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout_seconds: float = 1200.0,  # 20 min, covers deep mode
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.base_url = (base_url or os.getenv("AXL_BASE_URL", "http://localhost:8000")).rstrip("/")
        self.timeout = timeout_seconds
        # `transport` is for tests — inject an ASGITransport wrapping the
        # AXL FastAPI app to do in-process end-to-end without a real server.
        self._transport = transport

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=self.timeout, transport=self._transport) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code >= 400:
                raise AXLError(
                    status_code=resp.status_code,
                    code=_extract_code(resp),
                    message=resp.text,
                    path=path,
                )
            return resp.json()

    async def analyze_verdict(
        self,
        question: str,
        user_context: dict[str, Any] | None = None,
        options: list[str] | None = None,
        depth: Depth = "standard",
    ) -> VerdictResponse:
        payload = {
            "question": question,
            "user_context": user_context or {},
            "options": options,
            "depth": depth,
            "stream": False,
        }
        data = await self._post("/axl/v1/analyze/verdict", payload)
        return VerdictResponse.model_validate(data)

    async def analyze_estimate(
        self,
        question: str,
        user_context: dict[str, Any] | None = None,
        dimensions: list[str] | None = None,
        depth: Depth = "standard",
    ) -> EstimateResponse:
        payload = {
            "question": question,
            "user_context": user_context or {},
            "dimensions": dimensions,
            "depth": depth,
            "stream": False,
        }
        data = await self._post("/axl/v1/analyze/estimate", payload)
        return EstimateResponse.model_validate(data)

    async def analyze_plan(
        self,
        question: str,
        user_context: dict[str, Any] | None = None,
        goal: str | None = None,
        constraints: list[str] | None = None,
        depth: Depth = "deep",
    ) -> PlanResponse:
        payload = {
            "question": question,
            "user_context": user_context or {},
            "goal": goal,
            "constraints": constraints or [],
            "depth": depth,
            "stream": False,
        }
        data = await self._post("/axl/v1/analyze/plan", payload)
        return PlanResponse.model_validate(data)


class AXLError(Exception):
    def __init__(self, status_code: int, code: str | None, message: str, path: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.path = path
        super().__init__(f"AXL {path} failed [{status_code} {code}]: {message[:200]}")


def _extract_code(resp: httpx.Response) -> str | None:
    try:
        body = resp.json()
        if isinstance(body, dict):
            detail = body.get("detail")
            if isinstance(detail, str):
                head = detail.split(":", 1)[0].strip()
                return head or None
            if isinstance(detail, dict):
                return detail.get("code")
    except Exception:  # noqa: BLE001 — defensive only
        pass
    return None
