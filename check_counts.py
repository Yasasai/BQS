from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity
from sqlalchemy import or_

db = SessionLocal()
try:
    total = db.query(Opportunity).count()
    unassigned = db.query(Opportunity).filter(
        or_(
            Opportunity.workflow_status.in_(['NEW', 'OPEN', '']),
            Opportunity.workflow_status.is_(None)
        )
    ).count()
    print(f"Total: {total}")
    print(f"Unassigned: {unassigned}")
    first = db.query(Opportunity).first()
    if first:
        print(f"First ID: {first.opp_id} (Type: {type(first.opp_id)})")
        print(f"First Status: {first.workflow_status}")
finally:
    db.close()
