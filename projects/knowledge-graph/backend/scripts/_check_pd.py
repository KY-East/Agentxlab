import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.db import SessionLocal
from app.models.paper import paper_discipline, Paper
from app.models import Discipline

db = SessionLocal()
pd_count = db.execute(paper_discipline.select()).fetchall()
paper_count = db.query(Paper).count()
disc_count = db.query(Discipline).count()
print(f"Papers: {paper_count}")
print(f"Disciplines: {disc_count}")
print(f"paper_discipline rows: {len(pd_count)}")
if len(pd_count) > 0:
    for row in pd_count[:10]:
        print(f"  paper_id={row[0]} discipline_id={row[1]}")
db.close()
