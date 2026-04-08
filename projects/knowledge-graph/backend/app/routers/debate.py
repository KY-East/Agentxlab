from __future__ import annotations

import json as _json

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import Discipline, Intersection
from app.models.debate import Debate, DebateAgent
from app.models.forum import ForumPost
from app.models.spark import Spark
from app.schemas import (
    DebateBrief,
    DebateCreate,
    DebateOut,
    MessageOut,
    ModeSuggestion,
    SuggestModeRequest,
)
from app.services.debate_engine import (
    MAX_ROUNDS,
    generate_agents,
    generate_summary,
    run_round,
    run_round_stream,
    suggest_mode,
)
from app.services.forum_auto import auto_create_debate_post

router = APIRouter(prefix="/api/debates", tags=["debates"])


def _load_debate(debate_id: int, db: Session) -> Debate:
    debate = (
        db.query(Debate)
        .options(
            selectinload(Debate.agents).selectinload(DebateAgent.discipline),
            selectinload(Debate.messages),
            selectinload(Debate.disciplines),
        )
        .get(debate_id)
    )
    if not debate:
        raise HTTPException(404, "Debate not found")
    return debate


@router.post("", response_model=DebateOut)
async def create_debate(body: DebateCreate, db: Session = Depends(get_db)):
    if body.mode not in ("free", "debate"):
        raise HTTPException(400, "mode must be 'free' or 'debate'")
    if body.mode == "debate" and not body.proposition:
        raise HTTPException(400, "debate mode requires a proposition")

    unique_ids = list(dict.fromkeys(body.discipline_ids))
    disciplines = (
        db.query(Discipline)
        .filter(Discipline.id.in_(unique_ids))
        .all()
    )
    if len(disciplines) != len(unique_ids):
        found_ids = {d.id for d in disciplines}
        missing = [i for i in unique_ids if i not in found_ids]
        raise HTTPException(400, f"Discipline IDs not found: {missing}")
    if len(disciplines) < 2:
        raise HTTPException(400, "At least 2 disciplines required")

    resolved_intersection_id = None
    if body.intersection_id is not None:
        ix = db.query(Intersection).get(body.intersection_id)
        if not ix:
            raise HTTPException(400, f"Intersection {body.intersection_id} not found")
        ix_disc_ids = {d.id for d in ix.disciplines}
        req_disc_ids = {d.id for d in disciplines}
        if ix_disc_ids != req_disc_ids:
            raise HTTPException(
                400,
                f"Intersection {body.intersection_id} does not match the requested disciplines",
            )
        resolved_intersection_id = ix.id

    lang = body.language if body.language in ("zh", "en") else "zh"
    if lang == "zh":
        title = " \u00d7 ".join((d.name_zh or d.name_en) for d in disciplines)
    else:
        title = " \u00d7 ".join(d.name_en for d in disciplines)

    debate = Debate(
        title=title,
        mode=body.mode,
        language=lang,
        proposition=body.proposition,
        status="active",
        intersection_id=resolved_intersection_id,
    )
    debate.disciplines = list(disciplines)
    db.add(debate)
    db.flush()

    agent_specs = await generate_agents(
        disciplines, body.mode, body.proposition,
        user_weights=body.discipline_weights,
        language=lang,
    )
    for spec in agent_specs:
        agent = DebateAgent(debate_id=debate.id, **spec)
        db.add(agent)

    db.commit()
    return DebateOut.model_validate(_load_debate(debate.id, db))


@router.get("", response_model=list[DebateBrief])
def list_debates(
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Debate).order_by(Debate.created_at.desc())
    if status:
        q = q.filter(Debate.status == status)
    return [DebateBrief.model_validate(d) for d in q.limit(50).all()]


@router.get("/{debate_id}", response_model=DebateOut)
def get_debate(debate_id: int, db: Session = Depends(get_db)):
    return DebateOut.model_validate(_load_debate(debate_id, db))


@router.post("/{debate_id}/rounds", response_model=list[MessageOut])
async def next_round(debate_id: int, db: Session = Depends(get_db)):
    debate = _load_debate(debate_id, db)
    if debate.status != "active":
        raise HTTPException(400, "Debate is not active")

    current = max((m.round_number for m in debate.messages), default=0) + 1
    if current > MAX_ROUNDS:
        raise HTTPException(400, f"Maximum round limit ({MAX_ROUNDS}) reached")

    new_msgs = await run_round(debate, db)
    db.commit()

    for m in new_msgs:
        db.refresh(m)
    return [MessageOut.model_validate(m) for m in new_msgs]


@router.post("/{debate_id}/rounds/stream")
async def next_round_stream(debate_id: int, db: Session = Depends(get_db)):
    """SSE endpoint — streams each agent's message as it is generated."""
    debate = _load_debate(debate_id, db)
    if debate.status != "active":
        raise HTTPException(400, "Debate is not active")

    current = max((m.round_number for m in debate.messages), default=0) + 1
    if current > MAX_ROUNDS:
        raise HTTPException(400, f"Maximum round limit ({MAX_ROUNDS}) reached")

    agent_map = {a.id: a.agent_name for a in debate.agents}
    total_speakers = sum(
        1 for a in debate.agents
        if not (a.persona == "moderator" and current == 1)
    )

    async def event_generator():
        idx = 0
        try:
            async for msg in run_round_stream(debate, db):
                idx += 1
                payload = {
                    "id": msg.id,
                    "agent_id": msg.agent_id,
                    "agent_name": agent_map.get(msg.agent_id, ""),
                    "role": msg.role,
                    "content": msg.content,
                    "round_number": msg.round_number,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None,
                    "index": idx,
                    "total": total_speakers,
                }
                yield f"data: {_json.dumps(payload, ensure_ascii=False)}\n\n"
            db.commit()
            done = {"done": True, "round_number": current, "max_rounds": MAX_ROUNDS}
            yield f"data: {_json.dumps(done)}\n\n"
        except Exception as exc:
            err = {"error": str(exc)}
            yield f"data: {_json.dumps(err)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/{debate_id}/round-info")
def round_info(debate_id: int, db: Session = Depends(get_db)):
    debate = _load_debate(debate_id, db)
    current = max((m.round_number for m in debate.messages), default=0)
    return {"current_round": current, "max_rounds": MAX_ROUNDS}


@router.post("/{debate_id}/summarize", response_model=DebateOut)
async def summarize_debate(debate_id: int, db: Session = Depends(get_db)):
    debate = _load_debate(debate_id, db)
    if debate.status == "completed":
        raise HTTPException(400, "Debate already summarized")
    if not debate.messages:
        raise HTTPException(400, "No messages to summarize")

    debate.status = "summarizing"
    db.flush()

    await generate_summary(debate, db)
    db.commit()

    return DebateOut.model_validate(_load_debate(debate_id, db))


@router.post("/suggest-mode", response_model=ModeSuggestion)
async def api_suggest_mode(body: SuggestModeRequest):
    if len(body.discipline_names) < 2:
        raise HTTPException(400, "At least 2 discipline names required")
    result = await suggest_mode(body.discipline_names)
    return ModeSuggestion(**result)


@router.post("/{debate_id}/share-to-forum")
def share_debate_to_forum(debate_id: int, db: Session = Depends(get_db)):
    """Manually trigger (or retrieve) the forum post linked to a completed debate."""
    debate = _load_debate(debate_id, db)
    if debate.status != "completed":
        raise HTTPException(400, "Debate must be completed before sharing")

    post = auto_create_debate_post(debate, db)
    db.commit()
    if not post:
        raise HTTPException(500, "Failed to create forum post")
    return {"post_id": post.id, "title": post.title}


@router.post("/{debate_id}/sparks/{spark_id}/request-experiment")
def request_experiment(debate_id: int, spark_id: int, db: Session = Depends(get_db)):
    """Create an experiment-request forum post from a spark."""
    debate = _load_debate(debate_id, db)
    spark = db.query(Spark).filter(Spark.id == spark_id, Spark.debate_id == debate_id).first()
    if not spark:
        raise HTTPException(404, "Spark not found")

    existing = (
        db.query(ForumPost)
        .filter(ForumPost.spark_id == spark.id, ForumPost.post_type == "experiment_request")
        .first()
    )
    if existing:
        return {"post_id": existing.id, "title": existing.title, "already_exists": True}

    disc_names = [d.name_zh or d.name_en for d in debate.disciplines]
    title = f"[Experiment] {spark.content[:80]}{'...' if len(spark.content) > 80 else ''}"
    content = (
        f"**Novelty Type:** {spark.novelty_type}\n"
        f"**Score:** {spark.novelty_score:.2f}\n\n"
        f"{spark.content}\n\n"
    )
    if spark.reasoning:
        content += f"**Reasoning:** {spark.reasoning}\n\n"
    content += f"---\n\n*From debate: {debate.title}*"

    post = ForumPost(
        user_id=None,
        title=title,
        content=content,
        zone="ai_generated",
        post_type="experiment_request",
        status="open",
        debate_id=debate_id,
        spark_id=spark.id,
        is_pinned=False,
        discipline_tags=_json.dumps(disc_names),
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return {"post_id": post.id, "title": post.title, "already_exists": False}
