
import sys
import os

# Ensure backend module can be found
sys.path.append(os.getcwd())

from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity, OpportunityAssignment
import json

def inspect_data():
    db = SessionLocal()
    try:
        # Check Assignments
        print("\n--- Assignments ---")
        assignments = db.query(OpportunityAssignment).all()
        for a in assignments:
            print(f"Opp: {a.opp_id} | User: {a.assigned_to_user_id} | Status: {a.status}")

        # Check Opportunities
        print("\n--- Opportunities (Unassigned Check) ---")
        opps = db.query(Opportunity).all()
        unassigned_count = 0
        for o in opps:
            # Filter for OPEN or NULL (unassigned candidates)
            status = o.workflow_status
            if status == 'OPEN' or status is None:
                unassigned_count += 1
                print(f"ID: {o.opp_id} | Status: {status}")
        
        print(f"\nTotal 'Unassigned' (OPEN/None) count in DB: {unassigned_count}")
        
    finally:
        db.close()

if __name__ == "__main__":
    inspect_data()
