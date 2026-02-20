
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from backend.app.core.database import SessionLocal
from backend.app.models import AppUser, Opportunity

def check_sa_assignments():
    db = SessionLocal()
    try:
        sa_id = 'sa-001'
        sa = db.query(AppUser).filter(AppUser.user_id == sa_id).first()
        if not sa:
            print(f"❌ User '{sa_id}' (John Doe) not found in DB.")
            return
            
        print(f"✅ Found SA John Doe (ID: {sa_id})")
        
        opps = db.query(Opportunity).filter(Opportunity.assigned_sa_id == sa_id).all()
        print(f"📊 Opportunities assigned to SA '{sa_id}': {len(opps)}")
        
        for o in opps:
            print(f"  - {o.opp_id} | Status: {o.workflow_status}")

    finally:
        db.close()

if __name__ == "__main__":
    check_sa_assignments()
