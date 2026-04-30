"""KPAX core analysis API — five-step flow.

POST /api/analyze/start       → parse question, return context fields
POST /api/analyze/context     → submit answers, get expert preview
POST /api/analyze/supplement  → optional extra info
POST /api/analyze/run         → SSE stream of the expert debate

─────────────────────────────────────────────────────────────────────
⚠️ DEPRECATED — LEGACY ROUTER, EXCEPTION-REGISTERED IN PROJECT.md §5.1
─────────────────────────────────────────────────────────────────────

This module violates hard rule #6 (KPAX ↔ AXL HTTP-only, no monorepo
imports):
  - `from app.db import SessionLocal`
  - `from app.models.debate import Debate, DebateAgent`
  - `from app.services.debate_engine import run_round_stream, ...`
  - writes rows directly into AXL's DB

It is kept alive under **path D** (Ken 2026-04-17) because the KPAX
frontend (7 files under `kpax/frontend/`) still depends on these
endpoints, and wholesale removal would break the dev/demo path before
the v0 deliberation-room UI is ready.

**Rules while this file exists**:
  1. NEW features MUST NOT land here. Land them in
     `kpax_svc/routers/v1_analyze.py` (one-shot) or the future
     `kpax_svc/routers/v1_session.py` (stateful, HTTP to AXL).
  2. Bug fixes are OK but must be minimal and logged.
  3. This file gets deleted together with `report.py`,
     `services/context_collector.py`, and `kpax_svc/__init__.py`'s
     sys.path hack on the day the path-B migration completes.

**Replacement trigger**: KPAX v0 frontend protocol PRD completion
(owner @cc) + AXL-side `kpax_router.py` gaining real streaming
endpoints (`/axl/v1/debate/stream`, `/axl/v1/debate/{id}/messages`).
Then @cursor runs path B and purges this whole legacy cluster.

See `kpax/backend/kpax_svc/legacy_routers_assessment.md` for the full
decision record.
"""

from __future__ import annotations

import json as _json
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import selectinload

from app.db import SessionLocal
from app.models.debate import Debate, DebateAgent
from kpax_svc.services import (
    question_parser,
    context_collector,
    expert_builder,
    report_generator,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


# ── Schemas ──────────────────────────────────────────────────────────

class StartRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2000)

class StartResponse(BaseModel):
    session_id: str
    question_type: str
    question_summary: str
    context_fields: list[dict]

class ContextRequest(BaseModel):
    session_id: str
    answers: dict

class ContextResponse(BaseModel):
    session_id: str
    experts: list[dict]
    analysis_angles: list[str]
    core_tension: str

class SupplementRequest(BaseModel):
    session_id: str
    text: str = Field(..., min_length=1, max_length=5000)

class RunRequest(BaseModel):
    session_id: str


# ── Endpoints ────────────────────────────────────────────────────────

@router.post("/start", response_model=StartResponse)
async def start_analysis(body: StartRequest):
    """Step 1: User submits a question. Returns tailored context fields."""
    parsed = await question_parser.parse_question(body.question)
    session = context_collector.create_session(body.question, parsed)

    return StartResponse(
        session_id=session.session_id,
        question_type=session.question_type,
        question_summary=session.question_summary,
        context_fields=session.context_fields,
    )


@router.post("/context", response_model=ContextResponse)
async def submit_context(body: ContextRequest):
    """Step 2: User submits background answers. Returns expert lineup preview."""
    session = context_collector.get_session(body.session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    context_collector.update_answers(body.session_id, body.answers)
    ctx_text = context_collector.build_prompt_context(session)

    lineup = await expert_builder.build_experts(session.question, ctx_text)
    context_collector.set_expert_lineup(body.session_id, lineup.get("experts", []))

    return ContextResponse(
        session_id=session.session_id,
        experts=lineup.get("experts", []),
        analysis_angles=lineup.get("analysis_angles", []),
        core_tension=lineup.get("core_tension", ""),
    )


@router.post("/supplement")
async def supplement(body: SupplementRequest):
    """Step 3 (optional): User adds more context."""
    session = context_collector.get_session(body.session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    context_collector.add_supplement(body.session_id, body.text)
    return {"session_id": session.session_id, "status": "supplement_added"}


@router.post("/run")
async def run_analysis(body: RunRequest):
    """Step 4: Start the expert debate. Returns SSE stream."""
    session = context_collector.get_session(body.session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    if not session.expert_lineup:
        raise HTTPException(400, "No expert lineup — submit context first")

    ctx_text = context_collector.build_prompt_context(session)

    agent_specs = expert_builder.experts_to_system_prompts(
        session.expert_lineup, session.question, ctx_text
    )

    db = SessionLocal()
    try:
        debate = Debate(
            title=f"KPAX: {session.question[:100]}",
            mode="free",
            language="zh",
            proposition=session.question,
            status="active",
        )
        db.add(debate)
        db.flush()

        for spec in agent_specs:
            agent = DebateAgent(debate_id=debate.id, **spec)
            db.add(agent)

        db.commit()
        db.refresh(debate)
        debate = (
            db.query(Debate)
            .options(
                selectinload(Debate.agents).selectinload(DebateAgent.discipline),
                selectinload(Debate.messages),
                selectinload(Debate.disciplines),
            )
            .get(debate.id)
        )

        context_collector.set_debate_id(session.session_id, debate.id)
    except Exception:
        db.rollback()
        db.close()
        raise

    agent_map = {a.id: a.agent_name for a in debate.agents}
    total_speakers = len([a for a in debate.agents if a.persona != "moderator"])

    async def event_generator():
        nonlocal db
        try:
            from app.services.debate_engine import run_round_stream, generate_summary

            for round_num in range(1, 4):
                if round_num > 1:
                    debate_fresh = (
                        db.query(Debate)
                        .options(
                            selectinload(Debate.agents).selectinload(DebateAgent.discipline),
                            selectinload(Debate.messages),
                            selectinload(Debate.disciplines),
                        )
                        .get(debate.id)
                    )
                else:
                    debate_fresh = debate

                round_event = {
                    "type": "round_start",
                    "round": round_num,
                    "total_rounds": 3,
                }
                yield f"data: {_json.dumps(round_event, ensure_ascii=False)}\n\n"

                idx = 0
                async for msg in run_round_stream(debate_fresh, db):
                    idx += 1
                    payload = {
                        "type": "message",
                        "id": msg.id,
                        "agent_id": msg.agent_id,
                        "agent_name": agent_map.get(msg.agent_id, ""),
                        "role": msg.role,
                        "content": msg.content,
                        "round_number": msg.round_number,
                        "index": idx,
                        "total": total_speakers,
                    }
                    yield f"data: {_json.dumps(payload, ensure_ascii=False)}\n\n"

                db.commit()

            summary_event = {"type": "generating_summary"}
            yield f"data: {_json.dumps(summary_event)}\n\n"

            debate_final = (
                db.query(Debate)
                .options(
                    selectinload(Debate.agents),
                    selectinload(Debate.messages),
                    selectinload(Debate.disciplines),
                )
                .get(debate.id)
            )
            await generate_summary(debate_final, db)
            db.commit()
            db.refresh(debate_final)

            summary_data = {
                "consensus": debate_final.summary_consensus or "",
                "disagreements": debate_final.summary_disagreements or "",
                "open_questions": debate_final.summary_open_questions or "",
                "directions": debate_final.summary_directions or "",
            }

            all_msgs = [
                {
                    "agent_name": agent_map.get(m.agent_id, m.role),
                    "role": m.role,
                    "content": m.content,
                    "round_number": m.round_number,
                }
                for m in debate_final.messages
            ]

            report_event = {"type": "generating_report"}
            yield f"data: {_json.dumps(report_event)}\n\n"

            report = await report_generator.generate_report(
                question=session.question,
                context_summary=ctx_text,
                debate_messages=all_msgs,
                debate_summary=summary_data,
            )
            context_collector.set_report(session.session_id, report)

            done_event = {
                "type": "done",
                "debate_id": debate.id,
                "report": report,
            }
            yield f"data: {_json.dumps(done_event, ensure_ascii=False)}\n\n"

        except Exception as exc:
            logger.exception("Error during KPAX analysis stream")
            err = {"type": "error", "error": str(exc)}
            yield f"data: {_json.dumps(err)}\n\n"
        finally:
            db.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
