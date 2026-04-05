"""Sync top-cited works from OpenAlex for all subfields.

This populates the paper_discipline table with real cross-discipline
paper associations, enabling the graph to show evidence-based edges.

Usage:
    cd backend
    python -m scripts.sync_openalex_works
"""
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
logging.basicConfig(level=logging.INFO, format="%(message)s")

from app.db import SessionLocal
from app.services.openalex import sync_all_works

db = SessionLocal()
try:
    stats = sync_all_works(db, per_subfield=20)
    print(f"\nDone: {stats}")
finally:
    db.close()
