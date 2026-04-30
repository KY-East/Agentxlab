"""KPAX v1 analyze router — HTTP-only, AXL over the wire.

Replaces `routers/analyze.py` (legacy, monorepo-import-based) with a
clean version that satisfies Ken 2026-04-15 hard rule #6: KPAX touches
AXL only through HTTP.

v1.3 schema updates (PRD §13.4 §13.5):
  - `wallet_id` → `wallet_address` rename for v2 on-chain migration
  - Ledger records `llm_cost_usd` (platform audit) alongside balance moves

Flow (v0, one-shot, no session state):
  POST /api/v1/analyze
    body: {question, user_context, wallet_address, depth}
    steps:
      1. classify question -> {kind, options/dimensions/goal/...}
      2. hash request + quote token cost
      3. charge wallet (rejects early if insufficient)
      4. call AXLClient based on kind
      5. on success: record llm_cost_usd + return
      6. on AXL failure: refund charge + raise

Legacy `routers/analyze.py` stays registered alongside this for
backward compat until Ken decides to retire it.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from kpax_svc.clients.axl_client import (
    AXLClient,
    AXLError,
    EstimateResponse,
    PlanResponse,
    VerdictResponse,
)
from kpax_svc.clients.llm_client import chat_completion as _llm_chat_completion
from kpax_svc.services import question_classifier
from kpax_svc.services.token_ledger import InsufficientBalance, TokenLedger

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/analyze", tags=["analyze_v1"])


# ── module-level singletons (v0 simplicity) ───────────────────────

_ledger = TokenLedger()
_axl = AXLClient()


# ── request / response schemas ────────────────────────────────────

Depth = Literal["quick", "standard", "deep"]


class AnalyzeRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=2000)
    user_context: dict[str, Any] = Field(default_factory=dict)
    wallet_address: str = Field(..., min_length=3)
    depth: Depth = "standard"


class AnalyzeResponse(BaseModel):
    route: Literal["verdict", "estimate", "plan"]
    output: dict[str, Any]           # raw AXL response JSON
    wallet_address: str
    balance_before: int
    balance_after: int
    cost_charged: int
    request_hash: str
    classifier_rationale: str


class BalanceResponse(BaseModel):
    wallet_address: str
    balance: int


# ── endpoints ─────────────────────────────────────────────────────

@router.post("", response_model=AnalyzeResponse)
async def analyze(body: AnalyzeRequest) -> AnalyzeResponse:
    request_hash = _hash_request(body)

    # 1. classify
    try:
        route = await question_classifier.classify(body.question, chat_fn=_chat_fn)
    except Exception as exc:  # classifier is best-effort
        logger.warning("classifier hard-failed, defaulting to verdict: %s", exc)
        route = question_classifier.ClassifiedRoute(
            kind="verdict", options=["做", "不做"], rationale=f"fallback: {exc}"
        )

    # 2. quote + 3. charge
    cost = _ledger.quote_charge(body.depth)
    balance_before = _ledger.balance(body.wallet_address)
    try:
        _ledger.charge(body.wallet_address, depth=body.depth, request_hash=request_hash)
    except InsufficientBalance as exc:
        raise HTTPException(402, f"insufficient_balance: need {cost}, have {balance_before}") from exc

    # 4. dispatch to AXL
    try:
        if route.kind == "verdict":
            resp: VerdictResponse | EstimateResponse | PlanResponse = await _axl.analyze_verdict(
                question=body.question,
                user_context=body.user_context,
                options=route.options,
                depth=body.depth,
            )
        elif route.kind == "estimate":
            resp = await _axl.analyze_estimate(
                question=body.question,
                user_context=body.user_context,
                dimensions=route.dimensions,
                depth=body.depth,
            )
        else:  # plan
            resp = await _axl.analyze_plan(
                question=body.question,
                user_context=body.user_context,
                goal=route.goal,
                constraints=route.constraints,
                depth=body.depth,
            )
    except AXLError as exc:
        _ledger.refund(body.wallet_address, amount=cost, request_hash=request_hash)
        logger.exception("AXL call failed, charge refunded")
        raise HTTPException(502, f"axl_failed: {exc}") from exc
    except Exception as exc:
        _ledger.refund(body.wallet_address, amount=cost, request_hash=request_hash)
        logger.exception("unexpected error during AXL call, charge refunded")
        raise HTTPException(500, f"analyze_failed: {exc}") from exc

    # 5. Platform-side audit of real LLM spend (PRD §13.5).
    # AXL response carries debate_trace.cost_usd; record to ledger even when
    # v0 main product is free, so we can reconcile cost / model mix later.
    try:
        axl_cost_usd = float(resp.debate_trace.cost_usd or 0.0)
        if axl_cost_usd > 0:
            _ledger.record_llm_cost(
                body.wallet_address,
                cost_usd=axl_cost_usd,
                request_hash=request_hash,
                note=f"route={route.kind}",
            )
    except (AttributeError, TypeError, ValueError) as exc:
        logger.warning("record_llm_cost skipped (bad debate_trace): %s", exc)

    balance_after = _ledger.balance(body.wallet_address)
    return AnalyzeResponse(
        route=route.kind,
        output=resp.model_dump(),
        wallet_address=body.wallet_address,
        balance_before=balance_before,
        balance_after=balance_after,
        cost_charged=cost,
        request_hash=request_hash,
        classifier_rationale=route.rationale,
    )


@router.get("/balance/{wallet_address}", response_model=BalanceResponse)
async def get_balance(wallet_address: str) -> BalanceResponse:
    return BalanceResponse(wallet_address=wallet_address, balance=_ledger.balance(wallet_address))


# ── helpers ───────────────────────────────────────────────────────

def _hash_request(body: AnalyzeRequest) -> str:
    """Deterministic hash of (question + context + depth) for logging.

    Not used for cache (spec §5). Used so KPAX can later answer
    "have I seen this exact request before, and what did it cost".
    """
    payload = {
        "q": body.question.strip(),
        "ctx": _canonical(body.user_context),
        "depth": body.depth,
    }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


def _canonical(d: dict[str, Any]) -> Any:
    if isinstance(d, dict):
        return {k: _canonical(v) for k, v in sorted(d.items())}
    if isinstance(d, list):
        return [_canonical(x) for x in d]
    return d


async def _chat_fn(messages, temperature, max_tokens) -> str:
    """Classifier LLM hook — wraps the KPAX-local llm_client.

    Tests can still inject a fake `chat_fn` by calling `question_classifier.classify`
    directly with their own callable.
    """
    return await _llm_chat_completion(
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
