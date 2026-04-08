from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Discipline
from app.schemas import DisciplineBrief, DisciplineCreate, DisciplineOut, ScholarBrief

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/disciplines", tags=["disciplines"])


def _build_tree(disciplines: list[Discipline], parent_id: int | None = None) -> list[DisciplineOut]:
    children_map: dict[int | None, list[Discipline]] = {}
    for d in disciplines:
        children_map.setdefault(d.parent_id, []).append(d)

    def _recurse(pid: int | None) -> list[DisciplineOut]:
        nodes = []
        for d in children_map.get(pid, []):
            nodes.append(
                DisciplineOut(
                    id=d.id,
                    name_en=d.name_en,
                    name_zh=d.name_zh,
                    parent_id=d.parent_id,
                    depth=d.depth,
                    works_count=d.works_count,
                    children=_recurse(d.id),
                    is_custom=d.is_custom,
                    created_by=d.created_by,
                )
            )
        return nodes

    return _recurse(parent_id)


@router.get("", response_model=list[DisciplineOut])
def get_discipline_tree(
    db: Session = Depends(get_db),
    user_id: int | None = Query(None),
):
    query = db.query(Discipline).filter(Discipline.depth <= 1)
    if user_id:
        query = query.filter(
            (Discipline.is_custom == False) | (Discipline.created_by == user_id)
        )
    else:
        query = query.filter(Discipline.is_custom == False)
    all_disciplines = query.order_by(Discipline.depth, Discipline.id).all()
    return _build_tree(all_disciplines, parent_id=None)


def _find_openalex_ancestor(db: Session, discipline: Discipline) -> Discipline | None:
    """Walk up the parent chain to find the nearest ancestor with an openalex_id."""
    cur = discipline
    while cur:
        if cur.openalex_id:
            return cur
        if cur.parent_id:
            cur = db.query(Discipline).get(cur.parent_id)
        else:
            break
    return None


def _ensure_ancestor_papers(db: Session, ancestor: Discipline, limit: int = 25) -> dict:
    """Sync papers from OpenAlex for an ancestor subfield if not already populated."""
    from app.models.paper import paper_discipline
    from sqlalchemy import func

    existing_count = db.query(func.count()).select_from(paper_discipline).filter(
        paper_discipline.c.discipline_id == ancestor.id
    ).scalar()

    if existing_count >= limit:
        return {"status": "already_synced", "count": existing_count}

    try:
        from app.services.openalex import sync_works
        stats = sync_works(db, ancestor.openalex_id, limit=limit)
        return {"status": "synced", **stats}
    except Exception as e:
        logger.warning("OpenAlex sync for %s failed: %s", ancestor.openalex_id, e)
        return {"status": "error", "error": str(e)}


@router.post("", response_model=DisciplineOut)
def create_custom_discipline(body: DisciplineCreate, db: Session = Depends(get_db)):
    if not body.created_by:
        raise HTTPException(400, "created_by is required for custom disciplines")
    if body.parent_id:
        parent = db.query(Discipline).get(body.parent_id)
        if not parent:
            raise HTTPException(404, "Parent discipline not found")
        depth = parent.depth + 1
    else:
        depth = 0
    d = Discipline(
        name_en=body.name_en,
        name_zh=body.name_zh,
        parent_id=body.parent_id,
        depth=depth,
        is_custom=True,
        created_by=body.created_by,
    )
    db.add(d)
    db.flush()

    oa_ancestor = _find_openalex_ancestor(db, d)
    sync_result = None
    if oa_ancestor:
        sync_result = _ensure_ancestor_papers(db, oa_ancestor)
        logger.info(
            "Created discipline '%s' under '%s' (openalex: %s), paper sync: %s",
            d.name_en, oa_ancestor.name_en, oa_ancestor.openalex_id, sync_result,
        )

    db.commit()
    db.refresh(d)
    return DisciplineOut(
        id=d.id,
        name_en=d.name_en,
        name_zh=d.name_zh,
        parent_id=d.parent_id,
        depth=d.depth,
        children=[],
        is_custom=True,
        created_by=d.created_by,
    )


@router.delete("/{discipline_id}")
def delete_custom_discipline(discipline_id: int, db: Session = Depends(get_db)):
    d = db.query(Discipline).get(discipline_id)
    if not d:
        raise HTTPException(404, "Discipline not found")
    if not d.is_custom:
        raise HTTPException(403, "Cannot delete built-in disciplines")
    db.delete(d)
    db.commit()
    return {"ok": True}


@router.get("/{discipline_id}", response_model=DisciplineOut)
def get_discipline(discipline_id: int, db: Session = Depends(get_db)):
    d = db.query(Discipline).get(discipline_id)
    if not d:
        raise HTTPException(404, "Discipline not found")
    children_flat = db.query(Discipline).filter(Discipline.parent_id == d.id).all()
    return DisciplineOut(
        id=d.id,
        name_en=d.name_en,
        name_zh=d.name_zh,
        parent_id=d.parent_id,
        depth=d.depth,
        is_custom=d.is_custom,
        created_by=d.created_by,
        children=[
            DisciplineOut(
                id=c.id, name_en=c.name_en, name_zh=c.name_zh,
                parent_id=c.parent_id, depth=c.depth, children=[],
                is_custom=c.is_custom, created_by=c.created_by,
            )
            for c in children_flat
        ],
    )


@router.get("/{discipline_id}/scholars", response_model=list[ScholarBrief])
def get_scholars_by_discipline(discipline_id: int, db: Session = Depends(get_db)):
    d = db.query(Discipline).get(discipline_id)
    if not d:
        raise HTTPException(404, "Discipline not found")
    return [ScholarBrief.model_validate(s) for s in d.scholars]
