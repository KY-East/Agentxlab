"""One-command data refresh: re-seed disciplines + sync OpenAlex papers.

Run after adding/modifying disciplines in import_from_markdown.py.

Usage:
    cd backend

    # Full refresh (clear + re-seed + sync papers):
    python -m scripts.refresh_data

    # Seed only (skip OpenAlex sync, faster):
    python -m scripts.refresh_data --skip-sync

    # Sync only (keep existing seed, just re-pull papers):
    python -m scripts.refresh_data --sync-only
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
        insert_custom_extensions,
        insert_scholars,
        insert_papers,
        insert_intersections,
        _clear_seed_data,
    )

    print("\n[1/3] SEED DATA")
    print("  Clearing old data...")
    _clear_seed_data(db)

    print("  Inserting OpenAlex taxonomy...")
    insert_openalex_taxonomy(db)

    print("  Inserting custom extensions...")
    insert_custom_extensions(db)

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


def step_sync(db, per_subfield: int = 25):
    """Step 2: Sync top-cited papers from OpenAlex for all subfields."""
    from app.services.openalex import sync_works

    subfields = db.query(Discipline).filter(
        Discipline.openalex_id.like("subfields/%")
    ).order_by(Discipline.id).all()

    print(f"\n[2/3] OPENALEX SYNC ({len(subfields)} subfields, {per_subfield} papers each)")

    totals = {"added": 0, "skipped": 0, "tags": 0, "done": 0, "errors": 0}
    t0 = time.time()

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
        time.sleep(0.15)

    elapsed = time.time() - t0
    print(f"  Done in {elapsed:.0f}s: +{totals['added']} papers, "
          f"+{totals['tags']} tags, {totals['errors']} errors")


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

    print("=" * 60)
    print("  REFRESH DATA")
    print("=" * 60)

    Base.metadata.create_all(engine)
    db = SessionLocal()

    try:
        if not sync_only:
            step_seed(db)
            db.commit()

        if not skip_sync:
            step_sync(db)
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
