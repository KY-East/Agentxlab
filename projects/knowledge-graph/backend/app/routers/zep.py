from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.discipline import Discipline
from app.models.scholar import Scholar
from app.services.zep_manager import (
    push_discipline_knowledge,
    push_scholar_knowledge,
    search_knowledge,
)

router = APIRouter(prefix="/api/zep", tags=["zep"])


@router.post("/push-disciplines")
def api_push_disciplines(limit: int = 50, db: Session = Depends(get_db)):
    """Push discipline knowledge into Zep."""
    disciplines = (
        db.query(Discipline)
        .filter(Discipline.openalex_id.isnot(None))
        .limit(limit)
        .all()
    )
    pushed = 0
    for d in disciplines:
        children_names = [c.name_en for c in d.children] if d.children else []
        try:
            push_discipline_knowledge(d.name_en, d.description or "", children_names)
            pushed += 1
        except Exception:
            continue
    return {"status": "ok", "pushed": pushed, "total": len(disciplines)}


@router.post("/push-scholars")
def api_push_scholars(limit: int = 30, db: Session = Depends(get_db)):
    """Push scholar knowledge into Zep."""
    scholars = (
        db.query(Scholar)
        .filter(Scholar.openalex_id.isnot(None))
        .limit(limit)
        .all()
    )
    pushed = 0
    for s in scholars:
        try:
            push_scholar_knowledge(s.name, s.affiliation, s.works_count, s.cited_by_count)
            pushed += 1
        except Exception:
            continue
    return {"status": "ok", "pushed": pushed, "total": len(scholars)}


@router.get("/search")
def api_search(query: str, limit: int = 5):
    """Search Zep knowledge graph."""
    results = search_knowledge(query, limit=limit)
    return {"results": results}
