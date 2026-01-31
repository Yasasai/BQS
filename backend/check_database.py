import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.database import SessionLocal, init_db
from backend.app.models import Opportunity, OpportunityAssignment, AppUser

print("=" * 60)
print("  DATABASE DATA INTEGRITY CHECK (V2)")
print("=" * 60)

init_db()
db = SessionLocal()

# 1. Total count
total = db.query(Opportunity).count()
print(f"📊 Total Opportunities in Table: {total}")

# 2. Total active
active = db.query(Opportunity).filter(Opportunity.is_active == True).count()
print(f"✅ Active Opportunities: {active}")

# 3. Unassigned logic: Count opportunities that have NO entry in OpportunityAssignment
# This is how the real system determines "Unassigned"
assigned_ids = [row[0] for row in db.query(OpportunityAssignment.opp_id).filter(OpportunityAssignment.status == 'ACTIVE').all()]
unassigned = db.query(Opportunity).filter(~Opportunity.opp_id.in_(assigned_ids)).count()

print(f"📋 'Unassigned' (No SA record): {unassigned}")

# 4. Check for 'SUBMITTED_FOR_REVIEW' status 
# This is what drives the Red Box (Review Workflow)
pending_review = db.query(Opportunity).filter(Opportunity.workflow_status == 'SUBMITTED_FOR_REVIEW').count()
print(f"🔴 Pending Review (workflow_status='SUBMITTED_FOR_REVIEW'): {pending_review}")

# 5. Sample records with their workflow_status
print("\n📝 Sample records (workflow status):")
samples = db.query(Opportunity).limit(5).all()
for s in samples:
    is_assigned = "YES" if s.opp_id in assigned_ids else "NO"
    print(f"   - {s.opp_name[:30]}... | Status: {s.workflow_status} | Assigned: {is_assigned}")

db.close()
print("\nCheck complete.")
