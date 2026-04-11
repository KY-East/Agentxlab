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
    a: int = Query(..., description="First discipline ID"),
    b: int = Query(..., description="Second discipline ID"),
    db: Session = Depends(get_db),
):
    disc_a = db.get(Discipline, a)
    disc_b = db.get(Discipline, b)
    if not disc_a or not disc_b:
        raise HTTPException(404, "Discipline not found")

    def _collect_topics(disc: Discipline) -> list[Discipline]:
        """If the node is already a leaf topic (no children with depth==2),
        return [itself]; otherwise expand its depth==2 children."""
        children = db.query(Discipline).filter(
            Discipline.parent_id == disc.id, Discipline.depth == 2
        ).all()
        return children if children else [disc]

    topics_a = _collect_topics(disc_a)
    topics_b = _collect_topics(disc_b)

    ta_ids = [t.id for t in topics_a]
    tb_ids = [t.id for t in topics_b]
    name_map = {t.id: t.name_en for t in topics_a + topics_b}

    both_are_topics = (len(topics_a) == 1 and topics_a[0].id == a
                       and len(topics_b) == 1 and topics_b[0].id == b)

    topic_pairs: list[TopicCrossPair] = []
    total = 0

    pd1 = paper_discipline.alias("pd1")
    pd2 = paper_discipline.alias("pd2")

    if both_are_topics and a != b:
        total = (
            db.query(func.count(func.distinct(pd1.c.paper_id)))
            .join(pd2, pd1.c.paper_id == pd2.c.paper_id)
            .filter(pd1.c.discipline_id == a, pd2.c.discipline_id == b)
            .scalar() or 0
        )
        if total > 0:
            topic_pairs.append(TopicCrossPair(
                topic_a_id=a,
                topic_a_name=name_map.get(a, "?"),
                topic_b_id=b,
                topic_b_name=name_map.get(b, "?"),
                shared_papers=total,
            ))
    elif len(ta_ids + tb_ids) >= 2:
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

    if total == 0 and not both_are_topics:
        total = (
            db.query(func.count(func.distinct(pd1.c.paper_id)))
            .join(pd2, pd1.c.paper_id == pd2.c.paper_id)
            .filter(pd1.c.discipline_id == a, pd2.c.discipline_id == b)
            .scalar() or 0
        )

    return EdgeDetail(
        subfield_a_id=a,
        subfield_a_name=disc_a.name_en,
        subfield_b_id=b,
        subfield_b_name=disc_b.name_en,
        total_papers=total,
        topic_pairs=topic_pairs,
    )
