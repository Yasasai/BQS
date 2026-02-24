
import os
import sys

# Change to project root
os.chdir(r"c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS")
sys.path.append(os.getcwd())

from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity, AppUser

def find_retailco():
    db = SessionLocal()
    try:
        opp = db.query(Opportunity).filter(Opportunity.opp_name.like('%RetailCo%')).first()
        if not opp:
            print("RetailCo NOT FOUND")
            # List all opps to help me find it
            all_opps = db.query(Opportunity).limit(5).all()
            print("Available Opps:")
            for o in all_opps:
                print(f" - {o.opp_name}")
            return

        print(f"Found: {opp.opp_id} | {opp.opp_name}")
        print(f"Status: {opp.workflow_status}")
        print(f"Assigned PH: {opp.assigned_practice_head_id}")
        print(f"Assigned SH: {opp.assigned_sales_head_id}")
        print(f"Assigned SA: {opp.assigned_sa_id}")
        print(f"Assigned SP: {opp.assigned_sp_id}")
        
    finally:
        db.close()

if __name__ == "__main__":
    find_retailco()
