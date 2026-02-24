
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

try:
    from backend.app.core.database import SessionLocal
    from backend.app.models import Opportunity
    
    db = SessionLocal()
    count = db.query(Opportunity).count()
    print(f"Total Opportunities in DB: {count}")
    
    sample = db.query(Opportunity).first()
    if sample:
        print(f"Sample: {sample.opp_name} ({sample.workflow_status})")
    
    db.close()
except Exception as e:
    print(f"Error: {e}")
