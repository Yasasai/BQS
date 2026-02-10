
import sys
import os
import json
import requests
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity, AppUser
from sqlalchemy import or_, and_

def run_diagnostic():
    db = SessionLocal()
    try:
        # 1. DATABASE LAYER CHECK
        print("--- 1. DATABASE LAYER ---")
        sarah = db.query(AppUser).filter(AppUser.display_name.ilike('%Sarah%')).first()
        if not sarah:
            print("❌ User 'Sarah' not found in DB.")
            return
        
        user_id = sarah.user_id
        print(f"✅ Found Sarah: ID={user_id}, Role={sarah.role}")
        
        all_assigned = db.query(Opportunity).filter(
            Opportunity.assigned_practice_head_id == user_id,
            Opportunity.is_active == True
        ).all()
        
        print(f"✅ DB: Total active opportunities assigned to Sarah: {len(all_assigned)}")
        if all_assigned:
            for o in all_assigned[:5]:
                print(f"   - {o.opp_id}: Status={o.workflow_status}, SA={o.assigned_sa_id}, PH_Appr={o.ph_approval_status}")

        # 2. API LAYER CHECK
        print("\n--- 2. API LAYER ---")
        base_url = "http://127.0.0.1:8000/api/opportunities"
        tabs = ['action-required', 'in-progress', 'review', 'completed']
        
        for tab in tabs:
            params = {
                'tab': tab,
                'user_id': user_id,
                'role': 'PH'
            }
            try:
                # We'll use a local session mock if server isn't running, 
                # but better to test the actual logic function from the router if possible.
                # Since I'm in a script, I'll import the function directly to test Logic.
                from backend.app.routers.opportunities import get_all_opportunities
                
                response = get_all_opportunities(db=db, tab=tab, user_id=user_id, role='PH', page=1, limit=10)
                print(f"✅ API (Internal Call) - Tab '{tab}': items={len(response['items'])}, total_count={response['total_count']}, header_counts={response['counts'].get(tab)}")
                
                # Double check the 'total_count' vs 'header_counts'
                if response['total_count'] != response['counts'].get(tab):
                    print(f"   ⚠️ WARNING: Pagination total_count ({response['total_count']}) mismatch with tab header count ({response['counts'].get(tab)})")

            except Exception as e:
                print(f"❌ API logic error for tab {tab}: {str(e)}")

    finally:
        db.close()

if __name__ == "__main__":
    run_diagnostic()
