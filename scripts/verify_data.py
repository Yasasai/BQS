
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from database import SessionLocal, Opportunity

def verify():
    db = SessionLocal()
    count = db.query(Opportunity).count()
    print(f"Total Opportunities in DB: {count}")
    
    opps = db.query(Opportunity).all()
    for o in opps:
        print(f" - {o.remote_id}: {o.name} [{o.workflow_status}]")
    db.close()

if __name__ == "__main__":
    verify()
