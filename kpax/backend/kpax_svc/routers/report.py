"""KPAX report API — retrieve and follow up on analysis reports.

─────────────────────────────────────────────────────────────────────
⚠️ DEPRECATED — LEGACY ROUTER, EXCEPTION-REGISTERED IN PROJECT.md §5.1
─────────────────────────────────────────────────────────────────────

Violates hard rule #6 via:
  - `from app.db import SessionLocal`
  - `from app.models.debate import Debate`
  - reads AXL's debate messages directly for followup analysis

Kept under **path D** (Ken 2026-04-17) because frontend
`components/Report.tsx` consumes `/api/report/{id}` and `/followup`.
New features MUST NOT land here — use `v1_analyze.py` or the future
`v1_session.py`. This file is deleted when path B migration completes.

See `kpax/backend/kpax_svc/legacy_routers_assessment.md`.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import selectinload

from app.db import SessionLocal
from app.models.debate import Debate
from kpax_svc.services import context_collector, report_generator

router = APIRouter(prefix="/api/report", tags=["report"])


class FollowUpRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2000)


@router.get("/{session_id}")
async def get_report(session_id: str):
    """Retrieve the analysis report for a given session."""
    session = context_collector.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    if not session.report:
        raise HTTPException(404, "Report not ready yet")

    return {
        "session_id": session.session_id,
        "question": session.question,
        "question_type": session.question_type,
        "question_summary": session.question_summary,
        "status": session.status,
        "report": session.report,
        "experts": session.expert_lineup,
    }


@router.post("/{session_id}/followup")
async def followup(session_id: str, body: FollowUpRequest):
    """Ask a follow-up question about the analysis."""
    session = context_collector.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    if not session.report:
        raise HTTPException(400, "No report to follow up on")

    messages: list[dict] = []
    if session.debate_id:
        db = SessionLocal()
        try:
            debate = (
                db.query(Debate)
                .options(
                    selectinload(Debate.agents),
                    selectinload(Debate.messages),
                )
                .get(session.debate_id)
            )
            if debate:
                agent_map = {a.id: a.agent_name for a in debate.agents}
                messages = [
                    {
                        "agent_name": agent_map.get(m.agent_id, m.role),
                        "role": m.role,
                        "content": m.content,
                        "round_number": m.round_number,
                    }
                    for m in debate.messages
                ]
        finally:
            db.close()

    result = await report_generator.generate_followup(
        report=session.report,
        followup_question=body.question,
        debate_messages=messages,
    )

    return {
        "session_id": session_id,
        "followup_question": body.question,
        "result": result,
    }
