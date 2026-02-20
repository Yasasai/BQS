
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from backend.app.core.database import SessionLocal
from backend.app.models import AppUser, Opportunity

def verify_ids():
    db = SessionLocal()
    try:
        sarah = db.query(AppUser).filter(AppUser.user_id == 'ph-001').first()
        opp_count = db.query(Opportunity).filter(Opportunity.assigned_practice_head_id == 'ph-001').count()
        
        with open("diag_final.txt", "w") as f:
            if sarah:
                f.write(f"USER 'ph-001' EXISTS: {sarah.display_name}\n")
            else:
                f.write("USER 'ph-001' DOES NOT EXIST\n")
            f.write(f"OPPORTUNITIES ASSIGNED TO 'ph-001': {opp_count}\n")
    finally:
        db.close()

if __name__ == "__main__":
    verify_ids()
