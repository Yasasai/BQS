
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from backend.app.core.database import SessionLocal
from backend.app.models import AppUser, Opportunity

def verify_final_alignment():
    db = SessionLocal()
    try:
        # Check Sarah with new ID
        ph_id = 'ph-001'
        sarah = db.query(AppUser).filter(AppUser.user_id == ph_id).first()
        if not sarah:
            print(f"❌ Error: User '{ph_id}' still not found in DB. Seeding might be needed.")
            return
            
        print(f"✅ Found Sarah in DB with ID: {ph_id}")
        
        # Check assignments
        total = db.query(Opportunity).filter(Opportunity.assigned_practice_head_id == ph_id).count()
        print(f"✅ Total Opportunities assigned to '{ph_id}': {total}")
        
        # Check Action Required (Waterfall logic simulation)
        from sqlalchemy import and_, or_
        filter_completed = Opportunity.ph_approval_status.in_(['APPROVED', 'REJECTED'])
        filter_review = and_(
             ~filter_completed,
             Opportunity.workflow_status.in_(['READY_FOR_REVIEW', 'UNDER_REVIEW', 'SUBMITTED', 'SUBMITTED_FOR_REVIEW']),
             Opportunity.ph_approval_status == 'PENDING'
        )
        filter_action = and_(
            ~filter_completed,
            ~filter_review,
            Opportunity.assigned_sa_id.is_(None),
            Opportunity.workflow_status.notin_(['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST'])
        )
        
        count_action = db.query(Opportunity).filter(
            Opportunity.assigned_practice_head_id == ph_id,
            filter_action
        ).count()
        
        print(f"✅ Action Required Count for Sarah: {count_action}")
        
        if total > 0 and count_action > 0:
            print("\n🎉 SUCCESS: Data is now visible and correctly categorized for Sarah!")
        elif total > 0:
             print("\nℹ️ Data exists but none in 'Action Required'. Check if they are in 'In Progress' or 'Review'.")
        else:
            print("\n⚠️ No data assigned to this ID in the DB. Need to assign some ops to 'ph-001'.")

    finally:
        db.close()

if __name__ == "__main__":
    verify_final_alignment()
