
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity, AppUser
from sqlalchemy import desc

def inspect_recent_assignments():
    db = SessionLocal()
    try:
        # Get the 10 most recently updated opportunities
        recent_opps = db.query(Opportunity).order_by(desc(Opportunity.crm_last_updated_at)).limit(10).all()
        
        print(f"{'Opp ID':<10} | {'Name':<30} | {'Status':<15} | {'PH ID':<10} | {'SH ID':<10} | {'SA ID':<10}")
        print("-" * 100)
        
        for opp in recent_opps:
            ph_name = "None"
            if opp.assigned_practice_head_id:
                ph_user = db.query(AppUser).filter(AppUser.user_id == opp.assigned_practice_head_id).first()
                if ph_user: ph_name = ph_user.display_name
            
            print(f"{opp.opp_id:<10} | {opp.opp_name[:30]:<30} | {opp.workflow_status or 'None':<15} | {ph_name:<10} | {opp.assigned_sales_head_id or 'None':<10} | {opp.assigned_sa_id or 'None':<10}")

    finally:
        db.close()

if __name__ == "__main__":
    inspect_recent_assignments()
