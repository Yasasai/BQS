
import sys
import os
from datetime import datetime
import uuid

# Ensure backend module can be found
sys.path.append(os.getcwd())

from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity, OpportunityAssignment

def seed_unassigned():
    db = SessionLocal()
    try:
        print("🌱 Seeding/Forcing an Unassigned Opportunity...")

        # 1. Try to find an existing opportunity to reset
        opp = db.query(Opportunity).first()
        
        if not opp:
            # Create one if none exist
            print("   No opportunities found. Creating new test opportunity...")
            opp = Opportunity(
                opp_id=str(uuid.uuid4()),
                opp_number="TEST-001",
                opp_name="Test Unassigned Opportunity",
                customer_name="Test Customer",
                deal_value=50000.0,
                workflow_status="NEW",
                crm_last_updated_at=datetime.utcnow(),
                is_active=True
            )
            db.add(opp)
            db.commit()
            print(f"   Created Opportunity: {opp.opp_id}")
        else:
            print(f"   Found existing Opportunity: {opp.opp_id} ({opp.opp_name})")
            
        # 2. Force status to NEW
        opp.workflow_status = "NEW"
        
        # 3. Remove any active assignments for this opp
        assignments = db.query(OpportunityAssignment).filter(
            OpportunityAssignment.opp_id == opp.opp_id,
            OpportunityAssignment.status == 'ACTIVE'
        ).all()
        
        if assignments:
            print(f"   Found {len(assignments)} active assignments. Revoking...")
            for a in assignments:
                a.status = 'REVOKED'
        else:
            print("   No active assignments to revoke.")
            
        db.commit()
        print("✅ Opportunity forced to UNASSIGNED state.")
        print("   Refresh dashboard to verify.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_unassigned()
