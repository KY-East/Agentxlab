"""
OpenAlex API integration — sync academic taxonomy, works, and authors.

OpenAlex hierarchy: Domain (4) → Field (26) → Subfield (254) → Topic (~4516)
We import Field + Subfield into the Discipline table.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.discipline import Discipline
from app.models.paper import Paper, paper_discipline
from app.models.scholar import Scholar

logger = logging.getLogger(__name__)

BASE_URL = "https://api.openalex.org"
PER_PAGE = 200


def _headers() -> dict[str, str]:
    h: dict[str, str] = {}
    if settings.openalex_email:
        h["User-Agent"] = f"mailto:{settings.openalex_email}"
    return h


def _get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    with httpx.Client(base_url=BASE_URL, headers=_headers(), timeout=60) as client:
        resp = client.get(path, params=params or {})
        resp.raise_for_status()
        return resp.json()


def _openalex_short_id(full_url: str) -> str:
    """'https://openalex.org/fields/17' -> 'fields/17'"""
    return full_url.replace("https://openalex.org/", "")


# ── Taxonomy sync ────────────────────────────────────────────────

def sync_taxonomy(db: Session) -> dict[str, int]:
    """Pull all Fields (26) and Subfields (254) from OpenAlex into Discipline table."""
    stats = {"fields_added": 0, "fields_skipped": 0, "subfields_added": 0, "subfields_skipped": 0}

    fields_data = _get("/fields", {"per_page": 50})
    field_cache: dict[str, Discipline] = {}

    for f in fields_data.get("results", []):
        oa_id = _openalex_short_id(f["id"])
        existing = db.query(Discipline).filter_by(openalex_id=oa_id).first()
        if existing:
            field_cache[oa_id] = existing
            stats["fields_skipped"] += 1
            continue

        by_name = db.query(Discipline).filter_by(name_en=f["display_name"]).first()
        if by_name:
            by_name.openalex_id = oa_id
            by_name.level = "field"
            by_name.works_count = f.get("works_count")
            db.flush()
            field_cache[oa_id] = by_name
            stats["fields_added"] += 1
            continue

        disc = Discipline(
            name_en=f["display_name"],
            openalex_id=oa_id,
            level="field",
            depth=0,
            works_count=f.get("works_count"),
        )
        db.add(disc)
        db.flush()
        field_cache[oa_id] = disc
        stats["fields_added"] += 1

    seen_names: set[str] = {d.name_en for d in field_cache.values()}

    page = 1
    while True:
        sf_data = _get("/subfields", {"per_page": PER_PAGE, "page": page})
        results = sf_data.get("results", [])
        if not results:
            break

        for sf in results:
            oa_id = _openalex_short_id(sf["id"])
            display_name = sf["display_name"]

            existing = db.query(Discipline).filter_by(openalex_id=oa_id).first()
            if existing:
                stats["subfields_skipped"] += 1
                seen_names.add(display_name)
                continue

            parent_oa_id = _openalex_short_id(sf["field"]["id"]) if sf.get("field") else None
            parent = field_cache.get(parent_oa_id) if parent_oa_id else None

            by_name = db.query(Discipline).filter_by(name_en=display_name).first()
            if by_name:
                by_name.openalex_id = oa_id
                by_name.level = "subfield"
                by_name.works_count = sf.get("works_count")
                if parent and not by_name.parent_id:
                    by_name.parent_id = parent.id
                db.flush()
                stats["subfields_added"] += 1
                seen_names.add(display_name)
                continue

            if display_name in seen_names:
                stats["subfields_skipped"] += 1
                continue

            disc = Discipline(
                name_en=display_name,
                openalex_id=oa_id,
                level="subfield",
                depth=1,
                parent_id=parent.id if parent else None,
                works_count=sf.get("works_count"),
            )
            db.add(disc)
            db.flush()
            stats["subfields_added"] += 1
            seen_names.add(display_name)

        page += 1
        if page > (sf_data["meta"]["count"] // PER_PAGE) + 1:
            break

    db.commit()
    logger.info("Taxonomy sync complete: %s", stats)
    return stats


# ── Works sync ───────────────────────────────────────────────────

def _full_openalex_url(short_id: str) -> str:
    """'subfields/1702' -> 'https://openalex.org/subfields/1702'"""
    if short_id.startswith("https://"):
        return short_id
    return f"https://openalex.org/{short_id}"


def _build_disc_cache(db: Session) -> dict[str, int]:
    """Map OpenAlex full URL -> local discipline ID for all levels (field/subfield/topic)."""
    cache: dict[str, int] = {}
    for d in db.query(Discipline).filter(Discipline.openalex_id.isnot(None)).all():
        full_url = _full_openalex_url(d.openalex_id)
        cache[full_url] = d.id
    return cache


def _upsert_paper(db: Session, w: dict, stats: dict[str, int]) -> Paper:
    """Insert or retrieve a paper from an OpenAlex work record."""
    oa_id = _openalex_short_id(w["id"])
    existing = db.query(Paper).filter_by(openalex_id=oa_id).first()
    if existing:
        stats["skipped"] += 1
        return existing

    paper = Paper(
        title=w.get("title", "Untitled")[:500],
        year=w.get("publication_year"),
        published_year=w.get("publication_year"),
        openalex_id=oa_id,
        doi=w.get("doi"),
        citation_count=w.get("cited_by_count"),
        paper_type="frontier" if (w.get("publication_year") or 0) >= 2020 else "classic",
        abstract=_reconstruct_abstract(w.get("abstract_inverted_index")),
    )
    db.add(paper)
    db.flush()
    stats["added"] += 1
    return paper


def _tag_paper_disciplines(
    db: Session, paper: Paper, topics: list[dict],
    disc_cache: dict[str, int], stats: dict[str, int],
) -> None:
    """Tag a paper with all matching discipline IDs (subfield + topic levels)."""
    existing_disc_ids = {
        row.discipline_id
        for row in db.execute(
            paper_discipline.select().where(paper_discipline.c.paper_id == paper.id)
        ).fetchall()
    }

    for topic in topics:
        score = int((topic.get("score", 0) or 0) * 100)

        sf_url = topic.get("subfield", {}).get("id", "")
        sf_disc_id = disc_cache.get(sf_url)
        if sf_disc_id and sf_disc_id not in existing_disc_ids:
            db.execute(paper_discipline.insert().values(
                paper_id=paper.id, discipline_id=sf_disc_id, score=score,
            ))
            existing_disc_ids.add(sf_disc_id)
            stats["tags"] += 1

        topic_url = topic.get("id", "")
        topic_disc_id = disc_cache.get(topic_url)
        if topic_disc_id and topic_disc_id not in existing_disc_ids:
            db.execute(paper_discipline.insert().values(
                paper_id=paper.id, discipline_id=topic_disc_id, score=score,
            ))
            existing_disc_ids.add(topic_disc_id)
            stats["tags"] += 1


def sync_works(db: Session, subfield_openalex_id: str, limit: int = 50) -> dict[str, int]:
    """Pull top-cited works for a given subfield from OpenAlex.

    For each paper, tags both subfield-level and topic-level disciplines.
    """
    stats = {"added": 0, "skipped": 0, "tags": 0}
    disc_cache = _build_disc_cache(db)

    short_id = subfield_openalex_id.replace("https://openalex.org/", "")
    data = _get("/works", {
        "filter": f"topics.subfield.id:{short_id}",
        "sort": "cited_by_count:desc",
        "per_page": min(limit, PER_PAGE),
    })

    for w in data.get("results", []):
        paper = _upsert_paper(db, w, stats)
        _tag_paper_disciplines(db, paper, w.get("topics", []), disc_cache, stats)

    db.commit()
    logger.info("Works sync for %s: %s", subfield_openalex_id, stats)
    return stats


def sync_topic_works(
    db: Session,
    topic_openalex_id: str,
    limit: int = 15,
    disc_cache: dict[str, int] | None = None,
) -> dict[str, int]:
    """Pull top-cited works for a specific topic from OpenAlex.

    Uses topics.id filter for precise topic-level paper retrieval.
    Tags papers with all subfield + topic disciplines found on each work.
    Pass disc_cache to avoid rebuilding on every call during batch sync.
    """
    stats = {"added": 0, "skipped": 0, "tags": 0}
    if disc_cache is None:
        disc_cache = _build_disc_cache(db)

    short_id = topic_openalex_id.replace("https://openalex.org/", "")
    oa_topic_id = short_id.replace("topics/", "T")
    data = _get("/works", {
        "filter": f"topics.id:{oa_topic_id}",
        "sort": "cited_by_count:desc",
        "per_page": min(limit, PER_PAGE),
    })

    for w in data.get("results", []):
        paper = _upsert_paper(db, w, stats)
        _tag_paper_disciplines(db, paper, w.get("topics", []), disc_cache, stats)

    db.commit()
    logger.info("Topic works sync for %s: %s", topic_openalex_id, stats)
    return stats


def sync_all_works(db: Session, per_subfield: int = 30) -> dict[str, int]:
    """Pull top-cited works for ALL subfields, storing cross-discipline tags.

    This builds the local intersection evidence base.
    """
    subfields = db.query(Discipline).filter(
        Discipline.openalex_id.like("subfields/%")
    ).all()

    totals = {"added": 0, "skipped": 0, "tags": 0, "subfields": 0, "errors": 0}

    for i, sf in enumerate(subfields):
        logger.info("[%d/%d] Syncing %s (%s)...", i + 1, len(subfields), sf.name_en, sf.openalex_id)
        try:
            s = sync_works(db, sf.openalex_id, limit=per_subfield)
            totals["added"] += s["added"]
            totals["skipped"] += s["skipped"]
            totals["tags"] += s["tags"]
            totals["subfields"] += 1
        except Exception as exc:
            logger.warning("Failed to sync %s: %s", sf.openalex_id, exc)
            totals["errors"] += 1

    logger.info("sync_all_works complete: %s", totals)
    return totals


def _reconstruct_abstract(inverted_index: dict | None) -> str | None:
    """OpenAlex stores abstracts as inverted index — reconstruct plain text."""
    if not inverted_index:
        return None
    word_positions: list[tuple[int, str]] = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort(key=lambda x: x[0])
    return " ".join(w for _, w in word_positions)


# ── Authors sync ─────────────────────────────────────────────────

def sync_authors_from_works(db: Session, limit: int = 50) -> dict[str, int]:
    """Extract unique authors from recently synced papers via OpenAlex."""
    stats = {"added": 0, "skipped": 0}

    papers = db.query(Paper).filter(
        Paper.openalex_id.isnot(None)
    ).order_by(Paper.citation_count.desc()).limit(limit).all()

    seen_oa_ids: set[str] = set()

    for paper in papers:
        try:
            data = _get(f"/works/{paper.openalex_id}")
        except Exception:
            continue

        for authorship in data.get("authorships", []):
            author_data = authorship.get("author", {})
            if not author_data or not author_data.get("id"):
                continue

            oa_id = _openalex_short_id(author_data["id"])
            if oa_id in seen_oa_ids:
                continue
            seen_oa_ids.add(oa_id)

            existing = db.query(Scholar).filter_by(openalex_id=oa_id).first()
            if existing:
                stats["skipped"] += 1
                continue

            institutions = authorship.get("institutions", [])
            affiliation_name = institutions[0].get("display_name", "") if institutions else ""

            scholar = Scholar(
                name=author_data.get("display_name", "Unknown"),
                openalex_id=oa_id,
                orcid=author_data.get("orcid"),
                affiliation=affiliation_name,
            )
            db.add(scholar)
            stats["added"] += 1

    db.commit()
    logger.info("Authors from works sync: %s", stats)
    return stats
