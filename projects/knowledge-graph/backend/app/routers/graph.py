from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Discipline
from app.models.paper import paper_discipline
from app.schemas import EdgeDetail, GraphData, TopicCrossPair
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


@router.get("/edge-detail", response_model=EdgeDetail)
def get_edge_detail(
    a: int = Query(..., description="First subfield discipline ID"),
    b: int = Query(..., description="Second subfield discipline ID"),
    db: Session = Depends(get_db),
):
    sf_a = db.get(Discipline, a)
    sf_b = db.get(Discipline, b)
    if not sf_a or not sf_b:
        raise HTTPException(404, "Discipline not found")

    topics_a = db.query(Discipline).filter(
        Discipline.parent_id == a, Discipline.depth == 2
    ).all()
    topics_b = db.query(Discipline).filter(
        Discipline.parent_id == b, Discipline.depth == 2
    ).all()

    ta_ids = [t.id for t in topics_a]
    tb_ids = [t.id for t in topics_b]
    name_map = {t.id: t.name_en for t in topics_a + topics_b}

    if a == b:
        all_ids = ta_ids
    else:
        all_ids = ta_ids + tb_ids

    topic_pairs: list[TopicCrossPair] = []
    total = 0

    if len(all_ids) >= 2:
        pd1 = paper_discipline.alias("pd1")
        pd2 = paper_discipline.alias("pd2")

        if a == b:
            rows = (
                db.query(
                    pd1.c.discipline_id, pd2.c.discipline_id,
                    func.count(func.distinct(pd1.c.paper_id)),
                )
                .join(pd2, pd1.c.paper_id == pd2.c.paper_id)
                .filter(
                    pd1.c.discipline_id.in_(ta_ids),
                    pd2.c.discipline_id.in_(ta_ids),
                    pd1.c.discipline_id < pd2.c.discipline_id,
                )
                .group_by(pd1.c.discipline_id, pd2.c.discipline_id)
                .all()
            )
        else:
            rows = (
                db.query(
                    pd1.c.discipline_id, pd2.c.discipline_id,
                    func.count(func.distinct(pd1.c.paper_id)),
                )
                .join(pd2, pd1.c.paper_id == pd2.c.paper_id)
                .filter(
                    pd1.c.discipline_id.in_(ta_ids),
                    pd2.c.discipline_id.in_(tb_ids),
                )
                .group_by(pd1.c.discipline_id, pd2.c.discipline_id)
                .all()
            )

        for d1, d2, cnt in rows:
            if cnt > 0:
                topic_pairs.append(TopicCrossPair(
                    topic_a_id=d1,
                    topic_a_name=name_map.get(d1, "?"),
                    topic_b_id=d2,
                    topic_b_name=name_map.get(d2, "?"),
                    shared_papers=cnt,
                ))
                total += cnt

        topic_pairs.sort(key=lambda x: x.shared_papers, reverse=True)

    if total == 0:
        pd1 = paper_discipline.alias("pd1")
        pd2 = paper_discipline.alias("pd2")
        total = (
            db.query(func.count(func.distinct(pd1.c.paper_id)))
            .join(pd2, pd1.c.paper_id == pd2.c.paper_id)
            .filter(pd1.c.discipline_id == a, pd2.c.discipline_id == b)
            .scalar() or 0
        )

    return EdgeDetail(
        subfield_a_id=a,
        subfield_a_name=sf_a.name_en,
        subfield_b_id=b,
        subfield_b_name=sf_b.name_en,
        total_papers=total,
        topic_pairs=topic_pairs,
    )
