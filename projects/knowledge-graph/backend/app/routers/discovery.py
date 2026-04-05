"""Reverse Discovery: research question → discipline recommendations."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.db import get_db
from app.schemas import DiscoverRequest, DiscoveryResult
from app.services.reverse_discovery import discover
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/discover", tags=["discovery"])


@router.post("", response_model=DiscoveryResult)
async def reverse_discover(body: DiscoverRequest, db: Session = Depends(get_db)):
    question = body.question.strip()
    if not question:
        raise HTTPException(400, "question is required")

    try:
        raw_result = await discover(question, db)
    except ValueError as exc:
        raise HTTPException(502, str(exc)) from exc

    return DiscoveryResult(
        question=question,
        matched_disciplines=raw_result.get("matched_disciplines", []),
        recommended_combos=raw_result.get("recommended_combos", []),
    )
