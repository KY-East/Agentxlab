"""Paper generation: outline -> edit -> section-by-section writing -> export."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models.debate import Debate
from app.models.paper_draft import PaperDraft, PaperSection
from app.schemas import DraftBrief, DraftCreate, DraftOut, DraftUpdate, SectionOut
from app.services.paper_generator import (
    export_markdown,
    generate_all_sections,
    generate_outline,
    generate_section_content,
    refine_outline_via_chat,
    suggest_directions,
)

router = APIRouter(prefix="/api/papers/drafts", tags=["paper-generation"])


def _load_draft(draft_id: int, db: Session) -> PaperDraft:
    draft = (
        db.query(PaperDraft)
        .options(selectinload(PaperDraft.sections), selectinload(PaperDraft.debate))
        .get(draft_id)
    )
    if not draft:
        raise HTTPException(404, "Draft not found")
    return draft


@router.post("", response_model=DraftOut)
async def create_draft(body: DraftCreate, db: Session = Depends(get_db)):
    debate = (
        db.query(Debate)
        .options(selectinload(Debate.disciplines))
        .get(body.debate_id)
    )
    if not debate:
        raise HTTPException(404, "Debate not found")
    if debate.status != "completed":
        raise HTTPException(400, "Debate must be completed before generating a paper")

    direction = body.direction.strip()
    if not direction:
        raise HTTPException(400, "direction is required")

    draft = await generate_outline(debate, direction, db)
    db.commit()

    return DraftOut.model_validate(_load_draft(draft.id, db))


@router.get("", response_model=list[DraftBrief])
def list_drafts(debate_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(PaperDraft).order_by(PaperDraft.created_at.desc())
    if debate_id is not None:
        q = q.filter(PaperDraft.debate_id == debate_id)
    return [DraftBrief.model_validate(d) for d in q.limit(50).all()]


@router.get("/{draft_id}", response_model=DraftOut)
def get_draft(draft_id: int, db: Session = Depends(get_db)):
    return DraftOut.model_validate(_load_draft(draft_id, db))


@router.patch("/{draft_id}", response_model=DraftOut)
def update_draft(draft_id: int, body: DraftUpdate, db: Session = Depends(get_db)):
    draft = _load_draft(draft_id, db)

    if body.title is not None:
        draft.title = body.title

    if body.sections is not None:
        existing = {s.id: s for s in draft.sections}

        for sec_update in body.sections:
            if sec_update.id and sec_update.id in existing:
                s = existing[sec_update.id]
                if sec_update.heading is not None:
                    s.heading = sec_update.heading
                if sec_update.summary is not None:
                    s.summary = sec_update.summary
                if sec_update.writing_instruction is not None:
                    s.writing_instruction = sec_update.writing_instruction
                if sec_update.sort_order is not None:
                    s.sort_order = sec_update.sort_order
            elif not sec_update.id:
                new_sec = PaperSection(
                    draft_id=draft.id,
                    heading=sec_update.heading or "New Section",
                    summary=sec_update.summary,
                    writing_instruction=sec_update.writing_instruction,
                    sort_order=sec_update.sort_order if sec_update.sort_order is not None else len(draft.sections),
                    status="pending",
                )
                db.add(new_sec)
            else:
                raise HTTPException(
                    422,
                    f"Section id={sec_update.id} does not belong to draft {draft_id}",
                )

    db.commit()
    return DraftOut.model_validate(_load_draft(draft_id, db))


@router.post("/{draft_id}/sections/{section_id}/generate", response_model=SectionOut)
async def generate_section(
    draft_id: int, section_id: int, db: Session = Depends(get_db)
):
    draft = _load_draft(draft_id, db)

    section = db.query(PaperSection).get(section_id)
    if not section or section.draft_id != draft.id:
        raise HTTPException(404, "Section not found in this draft")

    debate = (
        db.query(Debate)
        .options(selectinload(Debate.disciplines))
        .get(draft.debate_id)
    )
    if not debate:
        raise HTTPException(404, "Associated debate not found")

    draft.debate = debate
    section = await generate_section_content(draft, section, db)
    db.commit()

    return SectionOut.model_validate(section)


@router.get("/{draft_id}/export")
def export_draft(draft_id: int, db: Session = Depends(get_db)):
    draft = _load_draft(draft_id, db)
    md = export_markdown(draft)
    return PlainTextResponse(md, media_type="text/markdown")


# ── Conversational paper flow ────────────────────────────────────


class SuggestDirectionsRequest(BaseModel):
    debate_id: int


@router.post("/suggest-directions")
async def api_suggest_directions(
    body: SuggestDirectionsRequest, db: Session = Depends(get_db)
):
    debate = (
        db.query(Debate)
        .options(selectinload(Debate.disciplines))
        .get(body.debate_id)
    )
    if not debate:
        raise HTTPException(404, "Debate not found")
    if debate.status != "completed":
        raise HTTPException(400, "Debate must be completed first")

    directions = await suggest_directions(debate, db)
    return {"directions": directions}


class ChatRefineRequest(BaseModel):
    debate_id: int
    current_title: str
    current_sections: list[dict]
    message: str


@router.post("/chat-refine")
async def api_chat_refine(body: ChatRefineRequest, db: Session = Depends(get_db)):
    debate = (
        db.query(Debate)
        .options(selectinload(Debate.disciplines))
        .get(body.debate_id)
    )
    if not debate:
        raise HTTPException(404, "Debate not found")

    result = await refine_outline_via_chat(
        debate=debate,
        current_title=body.current_title,
        current_sections=body.current_sections,
        user_message=body.message,
        db=db,
    )
    return result


@router.post("/{draft_id}/generate-all")
async def api_generate_all(draft_id: int, db: Session = Depends(get_db)):
    draft = _load_draft(draft_id, db)

    async def event_stream():
        async for event in generate_all_sections(draft, db):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
