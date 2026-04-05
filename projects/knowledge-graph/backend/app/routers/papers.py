from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Paper
from app.schemas import PaperOut

router = APIRouter(prefix="/api/papers", tags=["papers"])


@router.get("/{paper_id}", response_model=PaperOut)
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    p = db.query(Paper).get(paper_id)
    if not p:
        raise HTTPException(404, "Paper not found")
    return PaperOut.model_validate(p)
