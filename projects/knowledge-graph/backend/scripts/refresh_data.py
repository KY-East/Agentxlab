"""One-command data refresh: re-seed disciplines + sync OpenAlex papers.

Run after adding/modifying disciplines in import_from_markdown.py.

Usage:
    cd backend

    # Full refresh (clear + re-seed + sync papers at subfield + topic level):
    python -m scripts.refresh_data

    # Seed only (skip OpenAlex sync, faster):
    python -m scripts.refresh_data --skip-sync

    # Sync only (keep existing seed, just re-pull papers):
    python -m scripts.refresh_data --sync-only

    # Topic sync only (skip re-seed and subfield sync, just pull topic-level papers):
    python -m scripts.refresh_data --topics-only
"""
import sys
import time
import logging

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

from app.db import SessionLocal, engine
from app.models.base import Base
from app.models import Discipline
from app.models.paper import Paper, paper_discipline
from app.models.intersection import Intersection
from app.models.scholar import Scholar
from sqlalchemy import func


def step_seed(db):
    """Step 1: Clear old seed data and re-import taxonomy + scholars + papers + intersections."""
    from scripts.import_from_markdown import (
        insert_openalex_taxonomy,
        insert_scholars,
        insert_papers,
        insert_intersections,
        _clear_seed_data,
    )

    print("\n[1/3] SEED DATA")
    print("  Clearing old data...")
    _clear_seed_data(db)

    print("  Inserting OpenAlex taxonomy (3-level: fields + subfields + topics)...")
    insert_openalex_taxonomy(db)

    print("  Inserting scholars...")
    insert_scholars(db)

    print("  Inserting classic papers...")
    insert_papers(db)

    print("  Inserting intersections...")
    insert_intersections(db)

    db.flush()

    disc_count = db.query(Discipline).count()
    scholar_count = db.query(Scholar).count()
    paper_count = db.query(Paper).count()
    ix_count = db.query(Intersection).count()
    print(f"  Done: {disc_count} disciplines, {scholar_count} scholars, "
          f"{paper_count} papers, {ix_count} intersections")


def step_sync(db, per_subfield: int = 25, per_topic: int = 10, topics_only: bool = False):
    """Step 2: Sync top-cited papers from OpenAlex for subfields and topics."""
    from app.services.openalex import sync_works, sync_topic_works, _build_disc_cache

    totals = {"added": 0, "skipped": 0, "tags": 0, "done": 0, "errors": 0}
    t0 = time.time()

    if not topics_only:
        subfields = db.query(Discipline).filter(
            Discipline.openalex_id.like("subfields/%")
        ).order_by(Discipline.id).all()

        print(f"\n[2a/3] SUBFIELD SYNC ({len(subfields)} subfields, {per_subfield} papers each)")

        for i, sf in enumerate(subfields):
            print(f"  [{i+1}/{len(subfields)}] {sf.name_en}...", end=" ", flush=True)
            try:
                s = sync_works(db, sf.openalex_id, limit=per_subfield)
                totals["added"] += s["added"]
                totals["skipped"] += s["skipped"]
                totals["tags"] += s["tags"]
                totals["done"] += 1
                print(f"+{s['added']} papers, +{s['tags']} tags")
            except Exception as e:
                totals["errors"] += 1
                print(f"ERROR: {e}")
            time.sleep(0.12)

        db.commit()
        sf_elapsed = time.time() - t0
        print(f"  Subfield sync done in {sf_elapsed:.0f}s: +{totals['added']} papers, "
              f"+{totals['tags']} tags, {totals['errors']} errors")

    topics = db.query(Discipline).filter(
        Discipline.openalex_id.like("T%")
    ).order_by(Discipline.id).all()

    print(f"\n[2b/3] TOPIC SYNC ({len(topics)} topics, {per_topic} papers each)")
    print("  Building discipline cache...", flush=True)
    dc = _build_disc_cache(db)

    topic_totals = {"added": 0, "skipped": 0, "tags": 0, "done": 0, "errors": 0}
    t1 = time.time()

    for i, tp in enumerate(topics):
        if (i + 1) % 100 == 0 or i == 0:
            print(f"  [{i+1}/{len(topics)}] {tp.name_en}...", end=" ", flush=True)
        try:
            s = sync_topic_works(db, tp.openalex_id, limit=per_topic, disc_cache=dc)
            topic_totals["added"] += s["added"]
            topic_totals["skipped"] += s["skipped"]
            topic_totals["tags"] += s["tags"]
            topic_totals["done"] += 1
            if (i + 1) % 100 == 0 or i == 0:
                print(f"+{s['added']} papers, +{s['tags']} tags")
        except Exception as e:
            topic_totals["errors"] += 1
            if (i + 1) % 100 == 0 or i == 0:
                print(f"ERROR: {e}")
        time.sleep(0.12)

        if (i + 1) % 500 == 0:
            db.commit()

    db.commit()
    tp_elapsed = time.time() - t1
    print(f"\n  Topic sync done in {tp_elapsed:.0f}s: +{topic_totals['added']} papers, "
          f"+{topic_totals['tags']} tags, {topic_totals['errors']} errors")

    total_elapsed = time.time() - t0
    combined_added = totals["added"] + topic_totals["added"]
    combined_tags = totals["tags"] + topic_totals["tags"]
    combined_errors = totals["errors"] + topic_totals["errors"]
    print(f"  Total sync: {total_elapsed:.0f}s, +{combined_added} papers, "
          f"+{combined_tags} tags, {combined_errors} errors")


def step_report(db):
    """Step 3: Print final database stats."""
    print("\n[3/3] FINAL STATS")
    disc_count = db.query(Discipline).count()
    paper_count = db.query(Paper).count()
    ix_count = db.query(Intersection).count()
    total_papers = db.query(func.count(func.distinct(paper_discipline.c.paper_id))).scalar()
    total_tags = db.query(func.count()).select_from(paper_discipline).scalar()

    print(f"  Disciplines:        {disc_count}")
    print(f"  Papers (seed):      {paper_count}")
    print(f"  Papers (with OA):   {total_papers}")
    print(f"  Paper-discipline:   {total_tags} associations")
    print(f"  Intersections:      {ix_count}")
    print()


def main():
    skip_sync = "--skip-sync" in sys.argv
    sync_only = "--sync-only" in sys.argv
    topics_only = "--topics-only" in sys.argv

    print("=" * 60)
    print("  REFRESH DATA")
    print("=" * 60)

    Base.metadata.create_all(engine)
    db = SessionLocal()

    try:
        if not sync_only and not topics_only:
            step_seed(db)
            db.commit()

        if not skip_sync:
            step_sync(db, topics_only=topics_only)
            db.commit()

        step_report(db)

        print("All done.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
