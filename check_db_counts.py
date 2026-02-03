
from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity
from sqlalchemy import func

db = SessionLocal()
counts = db.query(Opportunity.is_active, func.count(Opportunity.opp_id)).group_by(Opportunity.is_active).all()
print(f"Counts by is_active: {counts}")

total = db.query(func.count(Opportunity.opp_id)).scalar()
print(f"Total opportunities: {total}")

workflow_counts = db.query(Opportunity.workflow_status, func.count(Opportunity.opp_id)).group_by(Opportunity.workflow_status).all()
print(f"Counts by workflow_status: {workflow_counts}")

db.close()
