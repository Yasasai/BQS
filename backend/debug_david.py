
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity, AppUser

def check_david_chen_assignments():
    db = SessionLocal()
    try:
        # 1. Find David Chen
        david = db.query(AppUser).filter(AppUser.display_name == "David Chen").first()
        if not david:
            print("❌ David Chen not found in AppUser table.")
            return

        print(f"✅ Found David Chen: ID={david.user_id}, Email={david.email}")

        # 2. Check Assignments
        assigned_opps = db.query(Opportunity).filter(Opportunity.assigned_practice_head_id == david.user_id).all()
        print(f"🔍 Opportunities assigned to PH ({david.user_id}): {len(assigned_opps)}")
        for o in assigned_opps:
            print(f"   - {o.opp_name} (ID: {o.opp_id})")

        # 3. Check Safety Hatch overlap (just curious)
        safety = db.query(Opportunity).filter(
            (Opportunity.opp_name.ilike('%RetailCo%')) | (Opportunity.opp_name.ilike('%Acme%'))
        ).all()
        print(f"🔍 Safety Hatch Items (Visible to all PHs): {len(safety)}")

    finally:
        db.close()

if __name__ == "__main__":
    check_david_chen_assignments()
