"""Build the force-directed graph payload from the database."""

from __future__ import annotations

from itertools import combinations

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.models import Discipline, Intersection
from app.models.paper import paper_discipline
from app.schemas import GraphData, GraphEdge, GraphNode


def _compute_root_ids(disciplines: list[Discipline], db: Session) -> dict[int, int]:
    """For each discipline, walk parent_id chain up to the top-level ancestor."""
    all_by_id: dict[int, Discipline] = {}

    parent_ids_needed = {d.parent_id for d in disciplines if d.parent_id is not None}
    ids_present = {d.id for d in disciplines}
    missing = parent_ids_needed - ids_present

    fetched = list(disciplines)
    while missing:
        ancestors = db.query(Discipline).filter(Discipline.id.in_(missing)).all()
        if not ancestors:
            break
        fetched.extend(ancestors)
        ids_present.update(a.id for a in ancestors)
        missing = {a.parent_id for a in ancestors if a.parent_id is not None} - ids_present

    for d in fetched:
        all_by_id[d.id] = d

    cache: dict[int, int] = {}

    def find_root(did: int) -> int:
        if did in cache:
            return cache[did]
        d = all_by_id.get(did)
        if not d or d.parent_id is None or d.parent_id not in all_by_id:
            cache[did] = did
            return did
        root = find_root(d.parent_id)
        cache[did] = root
        return root

    return {d.id: find_root(d.id) for d in disciplines}


def build_graph(db: Session, *, discipline_ids: list[int] | None = None) -> GraphData:
    """Return nodes and edges for D3 rendering.

    If *discipline_ids* is provided, only those disciplines appear as nodes
    and only intersections between them are shown. If empty or None, returns
    an empty graph (canvas starts blank, user picks disciplines).
    """
    if not discipline_ids:
        return GraphData(nodes=[], edges=[])

    disciplines = (
        db.query(Discipline)
        .filter(Discipline.id.in_(discipline_ids))
        .all()
    )

    disc_ids = {d.id for d in disciplines}
    root_ids = _compute_root_ids(disciplines, db)

    nodes = [
        GraphNode(
            id=d.id,
            name_en=d.name_en,
            name_zh=d.name_zh,
            depth=d.depth,
            parent_id=d.parent_id,
            root_id=root_ids.get(d.id),
        )
        for d in disciplines
    ]

    # --- Build ancestor map so children can match parent-level intersections ---
    disc_by_id: dict[int, Discipline] = {d.id: d for d in disciplines}

    def _ancestor_chain(d: Discipline) -> list[int]:
        chain = []
        cur = d
        while cur.parent_id:
            if cur.parent_id not in disc_by_id:
                parent = db.query(Discipline).get(cur.parent_id)
                if parent:
                    disc_by_id[parent.id] = parent
                    cur = parent
                    chain.append(cur.id)
                    continue
            elif cur.parent_id in disc_by_id:
                cur = disc_by_id[cur.parent_id]
                chain.append(cur.id)
                continue
            break
        return chain

    ancestor_to_selected: dict[int, set[int]] = {}
    for d in disciplines:
        ancestor_to_selected.setdefault(d.id, set()).add(d.id)
        for anc_id in _ancestor_chain(d):
            ancestor_to_selected.setdefault(anc_id, set()).add(d.id)

    # --- Edge source 1: hand-curated intersections ---
    intersections = (
        db.query(Intersection)
        .options(selectinload(Intersection.disciplines))
        .all()
    )
    _STATUS_PRIORITY = {"active": 0, "gap": 1}
    ix_edge_map: dict[tuple[int, int], Intersection] = {}
    for ix in intersections:
        all_member_ids = {d.id for d in ix.disciplines}
        representative: set[int] = set()
        used: set[int] = set()
        for mid in all_member_ids:
            candidates = (ancestor_to_selected.get(mid, set()) & disc_ids) - used
            if candidates:
                pick = min(candidates)
                representative.add(pick)
                used.add(pick)
        visible_members = sorted(representative)
        if len(visible_members) < 2:
            continue
        member_count = len(all_member_ids)
        ix_rank = (member_count, _STATUS_PRIORITY.get(ix.status, 9))
        for a, b in combinations(visible_members, 2):
            existing = ix_edge_map.get((a, b))
            if existing is None:
                ix_edge_map[(a, b)] = ix
            else:
                ex_members = len(existing.disciplines)
                ex_rank = (ex_members, _STATUS_PRIORITY.get(existing.status, 9))
                if ix_rank < ex_rank:
                    ix_edge_map[(a, b)] = ix

    # --- Edge source 2: shared papers (paper_discipline cross-count) ---
    # Custom L2/L3 leaves have no openalex_id, so no paper_discipline rows.
    # Map each selected disc to its nearest ancestor that has papers.
    # (disc_by_id already built above for ancestor_chain)

    def _paper_proxy(d: Discipline) -> int | None:
        """Walk up until we find an ancestor with openalex_id (has papers)."""
        cur = d
        while cur:
            if cur.openalex_id:
                return cur.id
            if cur.parent_id and cur.parent_id not in disc_by_id:
                parent = db.query(Discipline).get(cur.parent_id)
                if parent:
                    disc_by_id[parent.id] = parent
                    cur = parent
                    continue
            elif cur.parent_id:
                cur = disc_by_id[cur.parent_id]
                continue
            break
        return None

    leaf_to_proxy: dict[int, int] = {}
    proxy_ids: set[int] = set()
    for d in disciplines:
        p = _paper_proxy(d)
        if p is not None:
            leaf_to_proxy[d.id] = p
            proxy_ids.add(p)

    pd1 = paper_discipline.alias("pd1")
    pd2 = paper_discipline.alias("pd2")
    proxy_list = list(proxy_ids)
    proxy_paper_counts: dict[tuple[int, int], int] = {}
    if len(proxy_list) >= 2:
        rows = (
            db.query(
                pd1.c.discipline_id,
                pd2.c.discipline_id,
                func.count(func.distinct(pd1.c.paper_id)),
            )
            .join(pd2, pd1.c.paper_id == pd2.c.paper_id)
            .filter(
                pd1.c.discipline_id.in_(proxy_list),
                pd2.c.discipline_id.in_(proxy_list),
                pd1.c.discipline_id < pd2.c.discipline_id,
            )
            .group_by(pd1.c.discipline_id, pd2.c.discipline_id)
            .all()
        )
        for d1, d2, cnt in rows:
            proxy_paper_counts[(d1, d2)] = cnt

    paper_counts: dict[tuple[int, int], int] = {}
    for a, b in combinations(sorted(disc_ids), 2):
        pa = leaf_to_proxy.get(a)
        pb = leaf_to_proxy.get(b)
        if pa is not None and pb is not None and pa != pb:
            key = (min(pa, pb), max(pa, pb))
            pcount = proxy_paper_counts.get(key, 0)
            if pcount > 0:
                paper_counts[(a, b)] = pcount

    # --- Merge into edges ---
    all_pairs: set[tuple[int, int]] = set()
    for a, b in combinations(sorted(disc_ids), 2):
        all_pairs.add((a, b))

    edges = []
    for a, b in all_pairs:
        ix = ix_edge_map.get((a, b))
        pcount = paper_counts.get((a, b), 0)

        if ix:
            edges.append(GraphEdge(
                source=a, target=b,
                intersection_id=ix.id,
                title=ix.title,
                status=ix.status,
                weight=1,
                paper_count=pcount,
                core_tension=ix.core_tension,
            ))
        elif pcount > 0:
            edges.append(GraphEdge(
                source=a, target=b,
                intersection_id=None,
                title=f"{pcount} shared papers",
                status="evidence",
                weight=pcount,
                paper_count=pcount,
            ))

    return GraphData(nodes=nodes, edges=edges)
