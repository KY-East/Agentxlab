"""Detect research gaps — pairs of disciplines with no existing intersection."""

from __future__ import annotations

from itertools import combinations

from sqlalchemy.orm import Session

from app.models import Discipline, intersection_discipline


def find_gaps(db: Session, *, max_depth: int | None = None) -> list[dict]:
    """Return discipline pairs that have no active intersection.

    Only considers leaf disciplines (those with no children).
    """
    query = db.query(Discipline).filter(~Discipline.children.any())
    if max_depth is not None:
        query = query.filter(Discipline.depth <= max_depth)
    leaves = query.all()

    covered_pairs: set[tuple[int, int]] = set()
    rows = db.query(
        intersection_discipline.c.intersection_id,
        intersection_discipline.c.discipline_id,
    ).all()

    ix_discs: dict[int, list[int]] = {}
    for ix_id, d_id in rows:
        ix_discs.setdefault(ix_id, []).append(d_id)

    for discs in ix_discs.values():
        for a, b in combinations(sorted(discs), 2):
            covered_pairs.add((a, b))

    gaps = []
    leaf_list = sorted(leaves, key=lambda d: d.id)
    for a, b in combinations(leaf_list, 2):
        pair = (min(a.id, b.id), max(a.id, b.id))
        if pair not in covered_pairs:
            gaps.append(
                {
                    "disciplines": [
                        {"id": a.id, "name_en": a.name_en, "name_zh": a.name_zh},
                        {"id": b.id, "name_en": b.name_en, "name_zh": b.name_zh},
                    ]
                }
            )

    return gaps
