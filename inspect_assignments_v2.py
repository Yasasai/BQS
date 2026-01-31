
import sys
import os
import time

# Ensure backend module can be found
sys.path.append(os.getcwd())

from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity, OpportunityAssignment, AppUser

def inspect_data():
    sys.stdout.flush()
    db = SessionLocal()
    try:
        print("DATABASE INSPECTION START", flush=True)
        
        # Check Assignments
        print("\n--- Assignments ---", flush=True)
        assignments = db.query(OpportunityAssignment).all()
        print(f"Found {len(assignments)} assignment records", flush=True)
        
        for a in assignments:
            print(f"Opp: {a.opp_id} | UserID: {a.assigned_to_user_id} | Status: {a.status}", flush=True)
            
            # Check User existence
            user = db.query(AppUser).filter(AppUser.user_id == a.assigned_to_user_id).first()
            if not user:
                 print(f"   WARNING: User {a.assigned_to_user_id} NOT FOUND in AppUser table!", flush=True)
            else:
                 print(f"   User found: {user.display_name} ({user.email})", flush=True)

        # Check Opportunities
        print("\n--- Opportunities (Status Check) ---", flush=True)
        opps = db.query(Opportunity).all()
        assigned_count = 0
        for o in opps:
            if o.workflow_status == 'ASSIGNED_TO_SA':
                assigned_count += 1
                print(f"ID: {o.opp_id} | Name: {o.opp_name} | Status: {o.workflow_status} | AssignedSA: {o.assigned_sa}", flush=True)
        
        print(f"\nTotal 'ASSIGNED_TO_SA' count in DB: {assigned_count}", flush=True)
        
    except Exception as e:
        print(f"\nERROR: {e}", flush=True)
    finally:
        db.close()
        print("\nDone.", flush=True)

if __name__ == "__main__":
    inspect_data()
