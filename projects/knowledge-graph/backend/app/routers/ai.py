from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Discipline, Intersection, AIHypothesis
from app.schemas import (
    HypothesisOut,
    HypothesisRequest,
    ChatHypothesisRequest,
    ChatHypothesisResponse,
)
from app.services.ai_provider import generate_hypothesis, chat_hypothesis

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/hypothesis", response_model=HypothesisOut)
async def create_hypothesis(body: HypothesisRequest, db: Session = Depends(get_db)):
    unique_ids = list(dict.fromkeys(body.discipline_ids))
    disciplines = (
        db.query(Discipline)
        .filter(Discipline.id.in_(unique_ids))
        .all()
    )
    if len(disciplines) != len(unique_ids):
        raise HTTPException(400, "One or more discipline IDs not found")

    lang = body.language if body.language in ("zh", "en") else "zh"
    if lang == "zh":
        names = [(d.name_zh or d.name_en) for d in disciplines]
    else:
        names = [d.name_en for d in disciplines]
    text = await generate_hypothesis(names, model=body.model, language=lang)

    from app.models import intersection_discipline
    from sqlalchemy import func

    sorted_ids = sorted(unique_ids)
    n = len(sorted_ids)

    match_subq = (
        db.query(intersection_discipline.c.intersection_id)
        .filter(intersection_discipline.c.discipline_id.in_(sorted_ids))
        .group_by(intersection_discipline.c.intersection_id)
        .having(func.count() == n)
        .subquery()
    )

    total_subq = (
        db.query(
            intersection_discipline.c.intersection_id,
            func.count().label("total"),
        )
        .group_by(intersection_discipline.c.intersection_id)
        .subquery()
    )

    existing = (
        db.query(Intersection)
        .join(match_subq, Intersection.id == match_subq.c.intersection_id)
        .join(total_subq, Intersection.id == total_subq.c.intersection_id)
        .filter(total_subq.c.total == n)
        .filter(Intersection.status == "gap")
        .first()
    )

    if existing:
        ix = existing
    else:
        ix = Intersection(
            title=" x ".join(names),
            status="gap",
        )
        ix.disciplines = list(disciplines)
        db.add(ix)
        db.flush()

    hyp = AIHypothesis(
        intersection_id=ix.id,
        model_name=body.model or "default",
        prompt_used=f"Intersection: {' x '.join(names)}",
        hypothesis_text=text,
    )
    db.add(hyp)
    db.commit()
    db.refresh(hyp)

    try:
        from app.services.zep_manager import push_hypothesis
        push_hypothesis(names, text, body.model or "default")
    except Exception as e:
        logger.warning("Zep push after hypothesis failed: %s", e)

    return HypothesisOut.model_validate(hyp)


@router.post("/chat-hypothesis", response_model=ChatHypothesisResponse)
async def chat_hypothesis_endpoint(
    body: ChatHypothesisRequest,
    db: Session = Depends(get_db),
):
    ix = db.query(Intersection).filter(Intersection.id == body.intersection_id).first()
    if not ix:
        raise HTTPException(404, "Intersection not found")

    lang = body.language if body.language in ("zh", "en") else "zh"
    disc_names = []
    for d in ix.disciplines:
        disc_names.append((d.name_zh or d.name_en) if lang == "zh" else d.name_en)

    context_parts = []
    if ix.core_tension:
        context_parts.append(f"Core tension: {ix.core_tension}")
    if ix.open_questions:
        context_parts.append(f"Open questions: {ix.open_questions}")
    existing_hyps = (
        db.query(AIHypothesis)
        .filter(AIHypothesis.intersection_id == ix.id)
        .order_by(AIHypothesis.created_at.desc())
        .limit(2)
        .all()
    )
    for h in existing_hyps:
        context_parts.append(f"Previous hypothesis ({h.model_name}): {h.hypothesis_text[:300]}")
    context_text = "\n\n".join(context_parts) if context_parts else "No existing research context."

    result = await chat_hypothesis(
        discipline_names=disc_names,
        context_text=context_text,
        user_message=body.message,
        history=body.history,
        language=lang,
    )

    if result.get("hypothesis"):
        hyp = AIHypothesis(
            intersection_id=ix.id,
            model_name="chat",
            prompt_used=f"Chat: {body.message[:200]}",
            hypothesis_text=result["hypothesis"],
        )
        db.add(hyp)
        db.commit()

    return ChatHypothesisResponse(
        reply=result["reply"],
        hypothesis=result.get("hypothesis"),
        suggestions=result.get("suggestions", []),
    )
