
from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity

db = SessionLocal()
ph1_count = db.query(Opportunity).filter(Opportunity.assigned_practice_head_id == 'ph-001').count()
ph2_count = db.query(Opportunity).filter(Opportunity.assigned_practice_head_id == 'ph-002').count()
unassigned_count = db.query(Opportunity).filter(Opportunity.assigned_practice_head_id.is_(None)).count()
total = db.query(Opportunity).count()

print(f"Sarah Mitchell (ph-001): {ph1_count}")
print(f"David Chen (ph-002): {ph2_count}")
print(f"Unassigned to PH: {unassigned_count}")
print(f"Total: {total}")
db.close()
