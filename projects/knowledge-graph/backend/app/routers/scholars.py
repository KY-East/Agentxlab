from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Scholar
from app.schemas import ScholarOut

router = APIRouter(prefix="/api/scholars", tags=["scholars"])


@router.get("/{scholar_id}", response_model=ScholarOut)
def get_scholar(scholar_id: int, db: Session = Depends(get_db)):
    s = db.query(Scholar).get(scholar_id)
    if not s:
        raise HTTPException(404, "Scholar not found")
    return ScholarOut.model_validate(s)
