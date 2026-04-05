from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import GraphData
from app.services.graph import build_graph

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("", response_model=GraphData)
def get_graph(
    ids: str | None = Query(None, description="Comma-separated discipline IDs"),
    db: Session = Depends(get_db),
):
    discipline_ids = None
    if ids:
        discipline_ids = [int(x.strip()) for x in ids.split(",") if x.strip().isdigit()]
    return build_graph(db, discipline_ids=discipline_ids)
