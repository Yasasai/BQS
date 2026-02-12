from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.models import Opportunity
from app.core.database import DATABASE_URL

def verify_and_assign():
    engine = create_engine(DATABASE_URL)
    session = Session(engine)
    
    print(f"Connecting to: {DATABASE_URL}")
    
    target_names = ['RetailCo', 'Acme']
    
    for name in target_names:
        opps = session.query(Opportunity).filter(Opportunity.opp_name.ilike(f'%{name}%')).all()
        print(f"\nLooking for '{name}': Found {len(opps)} items")
        for opp in opps:
            print(f"  - ID: {opp.opp_id} | Name: {opp.opp_name}")
            print(f"    Status: {opp.workflow_status} | Active: {opp.is_active}")
            print(f"    PH: {opp.assigned_practice_head_id} | SH: {opp.assigned_sales_head_id}")
            
            # FORCE UPDATE
            opp.is_active = True
            opp.workflow_status = 'READY_FOR_REVIEW'
            opp.assigned_practice_head_id = 'ph-001'
            opp.assigned_sales_head_id = 'sh-001'
            opp.gh_approval_status = 'PENDING'
            opp.ph_approval_status = 'PENDING'
            opp.sh_approval_status = 'PENDING'
            
    session.commit()
    print("\n✅ Successfully updated target opportunities in PostgreSQL.")
    session.close()

if __name__ == "__main__":
    verify_and_assign()
