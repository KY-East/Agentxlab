from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.openalex import sync_taxonomy, sync_works, sync_authors_from_works

router = APIRouter(prefix="/api/openalex", tags=["openalex"])


@router.post("/sync-taxonomy")
def api_sync_taxonomy(db: Session = Depends(get_db)):
    """Pull all Fields + Subfields from OpenAlex into the Discipline table."""
    stats = sync_taxonomy(db)
    return {"status": "ok", "stats": stats}


@router.post("/sync-works/{subfield_id:path}")
def api_sync_works(subfield_id: str, limit: int = 50, db: Session = Depends(get_db)):
    """Pull top-cited works for a given subfield. subfield_id = e.g. 'subfields/1702'."""
    stats = sync_works(db, subfield_id, limit=limit)
    return {"status": "ok", "stats": stats}


@router.post("/sync-authors")
def api_sync_authors(limit: int = 50, db: Session = Depends(get_db)):
    """Extract authors from the top-cited papers already in DB."""
    stats = sync_authors_from_works(db, limit=limit)
    return {"status": "ok", "stats": stats}
