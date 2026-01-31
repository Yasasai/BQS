from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity, OpportunityAssignment

def check_assignments():
    db = SessionLocal()
    try:
        opps = db.query(Opportunity).all()
        print(f"Total Opportunities: {len(opps)}")
        for o in opps:
            assign = db.query(OpportunityAssignment).filter_by(opp_id=o.opp_id, status='ACTIVE').first()
            assign_str = f"Assigned to: {assign.assigned_to_user_id}" if assign else "UNASSIGNED"
            print(f"ID: {o.opp_id} | Name: {o.opp_name} | WorkflowStatus: {o.workflow_status} | {assign_str}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_assignments()
