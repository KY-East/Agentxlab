"""End-to-end smoke test for KPAX v1_analyze wired to AXL mock router.

Runs entirely in-process via httpx ASGITransport — no real server.
Exercises: axl_client, token_ledger, question_classifier, v1_analyze
router + AXL kpax_router mock.
"""
from __future__ import annotations

import asyncio
import json as _j
import os
import sys
import tempfile


def main() -> int:
    tmpdir = tempfile.mkdtemp(prefix="kpax_smoke_")
    os.environ["KPAX_LEDGER_JSONL"] = os.path.join(tmpdir, "ledger.jsonl")

    # ---- Test 1: axl_client direct --------------------------------
    from app.main import app as axl_app  # noqa: E402
    from httpx import ASGITransport  # noqa: E402
    from kpax_svc.clients.axl_client import AXLClient  # noqa: E402

    client = AXLClient(base_url="http://axl.test", transport=ASGITransport(app=axl_app))

    async def t1() -> None:
        v = await client.analyze_verdict(
            question="should I quit my job", options=["yes", "no"]
        )
        assert v.question_type == "verdict"
        assert len(v.options) == 2
        assert abs(sum(o.score for o in v.options) - 1.0) < 0.01
        assert v.debate_trace.rounds == 4
        assert v.meta.depth == "standard"

        e = await client.analyze_estimate(
            question="will brazil win wc 2026", dimensions=["champion probability"]
        )
        assert e.dimensions[0].kind == "probability"

        e2 = await client.analyze_estimate(
            question="how good is this offer",
            dimensions=["pay", "growth", "risk"],
        )
        assert e2.dimensions[0].kind == "score"
        assert len(e2.dimensions) == 3

        p = await client.analyze_plan(
            question="how to build saas from zero", depth="deep"
        )
        assert p.debate_trace.rounds == 5  # Ken-pinned deep=5
        assert p.phases[0].duration.start_month == 0

    asyncio.run(t1())
    print("[1/4] axl_client direct: PASS")

    # ---- Test 2: token_ledger unit --------------------------------
    from kpax_svc.services.token_ledger import (  # noqa: E402
        InMemoryJsonlStorage,
        InsufficientBalance,
        TokenLedger,
    )

    ledger = TokenLedger(storage=InMemoryJsonlStorage())
    wallet = "guest_smoke_001"
    assert ledger.balance(wallet) == 50, "guest seed"
    entry = ledger.charge(wallet, depth="standard", request_hash="abc123")
    assert entry.delta == -25
    assert ledger.balance(wallet) == 25

    try:
        ledger.charge(wallet, depth="deep", request_hash="x")
        raise AssertionError("should have raised")
    except InsufficientBalance:
        pass
    assert ledger.balance(wallet) == 25

    ledger.refund(wallet, amount=25, request_hash="abc123")
    assert ledger.balance(wallet) == 50

    ledger.reward_share(wallet)
    assert ledger.balance(wallet) == 70

    assert len(ledger.history(wallet)) == 4
    print("[2/4] token_ledger: PASS")

    # ---- Test 3: question_classifier ------------------------------
    from kpax_svc.services.question_classifier import classify  # noqa: E402

    async def fake_chat(messages, temperature, max_tokens):  # type: ignore[no-untyped-def]
        return _j.dumps(
            {
                "kind": "verdict",
                "options": ["a", "b"],
                "dimensions": None,
                "goal": None,
                "constraints": None,
                "rationale": "test",
            }
        )

    async def bad_chat(messages, temperature, max_tokens):  # type: ignore[no-untyped-def]
        return "no json here"

    async def t3() -> None:
        r = await classify("should I take this offer", chat_fn=fake_chat)
        assert r.kind == "verdict" and r.options == ["a", "b"]

        r2 = await classify("anything", chat_fn=bad_chat)
        assert r2.kind == "verdict" and "fallback" in r2.rationale

    asyncio.run(t3())
    print("[3/4] question_classifier: PASS")

    # ---- Test 4: KPAX v1_analyze end-to-end -----------------------
    import kpax_svc.routers.v1_analyze as v1  # noqa: E402

    v1._axl = AXLClient(base_url="http://axl.test", transport=ASGITransport(app=axl_app))
    v1._ledger = TokenLedger(storage=InMemoryJsonlStorage())

    from fastapi import FastAPI  # noqa: E402
    from fastapi.testclient import TestClient  # noqa: E402

    kpax_app = FastAPI()
    kpax_app.include_router(v1.router)
    tc = TestClient(kpax_app)

    # balance endpoint creates guest wallet
    r = tc.get("/api/v1/analyze/balance/guest_e2e_001")
    assert r.status_code == 200 and r.json()["balance"] == 50

    # full analyze flow (classifier falls back since _chat_fn raises NotImplementedError)
    r = tc.post(
        "/api/v1/analyze",
        json={
            "question": "should I quit my job and start a company",
            "user_context": {"age": 32},
            "wallet_address": "guest_e2e_001",
            "depth": "standard",
        },
    )
    assert r.status_code == 200, f"got {r.status_code}: {r.text[:300]}"
    body = r.json()
    assert body["route"] == "verdict"
    assert body["cost_charged"] == 25
    assert body["balance_before"] == 50
    assert body["balance_after"] == 25
    assert body["output"]["question_type"] == "verdict"
    assert len(body["request_hash"]) == 16

    # insufficient balance rejects cleanly, no refund drift
    r2 = tc.post(
        "/api/v1/analyze",
        json={
            "question": "another deep question here about life",
            "user_context": {},
            "wallet_address": "guest_e2e_001",
            "depth": "deep",  # cost 60 > have 25
        },
    )
    assert r2.status_code == 402, f"expected 402, got {r2.status_code}"
    assert v1._ledger.balance("guest_e2e_001") == 25

    print("[4/4] KPAX v1_analyze end-to-end: PASS")
    print()
    print("ALL SMOKE TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
