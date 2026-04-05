"""Sync top-cited works for ALL subfields to build the base knowledge graph.

Usage:
    cd backend
    python -m scripts.sync_all
"""
import sys, time, logging
sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

from app.db import SessionLocal
from app.models import Discipline
from app.models.paper import paper_discipline
from app.services.openalex import sync_works
from sqlalchemy import func

db = SessionLocal()

subfields = db.query(Discipline).filter(
    Discipline.openalex_id.like("subfields/%")
).order_by(Discipline.id).all()

print(f"Total subfields to sync: {len(subfields)}")

totals = {"added": 0, "skipped": 0, "tags": 0, "done": 0, "errors": 0}
t0 = time.time()

for i, sf in enumerate(subfields):
    print(f"[{i+1}/{len(subfields)}] {sf.name_en} ({sf.openalex_id})...", end=" ", flush=True)
    try:
        s = sync_works(db, sf.openalex_id, limit=25)
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
total_papers = db.query(func.count(func.distinct(paper_discipline.c.paper_id))).scalar()
total_tags = db.query(func.count()).select_from(paper_discipline).scalar()

print(f"\n{'='*60}")
print(f"Done in {elapsed:.0f}s")
print(f"Subfields: {totals['done']}/{len(subfields)} (errors: {totals['errors']})")
print(f"Papers added: {totals['added']}, skipped: {totals['skipped']}")
print(f"Tags added: {totals['tags']}")
print(f"Total in paper_discipline: {total_tags} tags across {total_papers} papers")

db.close()
