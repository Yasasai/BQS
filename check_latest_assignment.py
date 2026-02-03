
from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity, OppScoreVersion, OpportunityAssignment
from sqlalchemy import desc

db = SessionLocal()

# Find the most recently assigned opportunity
last_assignment = db.query(OpportunityAssignment).order_by(desc(OpportunityAssignment.assigned_at)).first()

if last_assignment:
    opp_id = last_assignment.opp_id
    opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    latest_ver = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == opp_id).order_by(desc(OppScoreVersion.version_no)).all()
    
    print(f"Opp ID: {opp_id}")
    print(f"Opp Name: {opp.opp_name}")
    print(f"Workflow Status: {opp.workflow_status}")
    print(f"Assigned to: {last_assignment.assigned_to_user_id}")
    print(f"Versions:")
    for v in latest_ver:
        print(f"  - Ver {v.version_no}: Status={v.status}, Overall={v.overall_score}, Created={v.created_at}")
else:
    print("No assignments found.")

db.close()
