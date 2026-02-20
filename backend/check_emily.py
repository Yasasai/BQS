
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity

def check_emily_assignments():
    db = SessionLocal()
    try:
        # Emily White is 'sp-001'
        print("🔍 Checking assignments for Emily White (sp-001)...")
        opps = db.query(Opportunity).filter(Opportunity.assigned_sp_id == 'sp-001').all()
        
        if not opps:
            print("❌ Emily has NO assignments.")
            # Let's assign one for testing
            first_opp = db.query(Opportunity).first()
            if first_opp:
                print(f"Assigning {first_opp.opp_id} ({first_opp.opp_name}) to sp-001")
                first_opp.assigned_sp_id = 'sp-001'
                db.commit()
                print("✅ Assigned.")
        else:
            print(f"✅ Emily has {len(opps)} assignments:")
            for o in opps:
                print(f"  - {o.opp_id}: {o.name} [Status: {o.workflow_status}]")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_emily_assignments()
