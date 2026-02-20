
from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity
from sqlalchemy import func

db = SessionLocal()
total = db.query(Opportunity).count()
active = db.query(Opportunity).filter(Opportunity.is_active == True).count()
unassigned_gh = db.query(Opportunity).filter(
    Opportunity.assigned_practice_head_id == None, 
    Opportunity.assigned_sales_head_id == None,
    Opportunity.is_active == True
).count()

print(f"Total rows: {total}")
print(f"Active rows: {active}")
print(f"GH Unassigned (Active): {unassigned_gh}")

# Sample statuses
stats = db.query(Opportunity.workflow_status, func.count(Opportunity.opp_id)).group_by(Opportunity.workflow_status).all()
print("Statuses:")
for s, c in stats:
    print(f"  {s}: {c}")

db.close()
