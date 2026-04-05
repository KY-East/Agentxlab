from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.gaps import find_gaps

router = APIRouter(prefix="/api/gaps", tags=["gaps"])


@router.get("")
def list_gaps(db: Session = Depends(get_db)):
    return find_gaps(db)
