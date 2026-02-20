
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from backend.app.core.database import SessionLocal
from backend.app.models import AppUser, Opportunity

def check_user_ids():
    db = SessionLocal()
    results = []
    try:
        results.append("--- APP USERS IN DB ---")
        users = db.query(AppUser).all()
        for u in users:
            results.append(f"ID: {u.user_id} | Name: {u.display_name} | Role: {u.role}")
            
        results.append("\n--- OPPORTUNITIES PH ASSIGNMENTS ---")
        ph_assignments = db.query(Opportunity.assigned_practice_head_id).filter(Opportunity.assigned_practice_head_id.isnot(None)).distinct().all()
        results.append(f"Unique PH IDs assigned in Opportunities table: {[r[0] for r in ph_assignments]}")
        
        with open("diag_results.txt", "w") as f:
            f.write("\n".join(results))
            
    finally:
        db.close()

if __name__ == "__main__":
    check_user_ids()
