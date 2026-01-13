import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from database import SessionLocal, Opportunity

def check_db():
    db = SessionLocal()
    try:
        opps = db.query(Opportunity).all()
        print(f"Total Chances: {len(opps)}")
        if opps:
            print("\nSample Data (Last 3):")
            for opp in opps[-3:]:
                print(f"ID: {opp.remote_id} | Name: {opp.name} | Status: {opp.workflow_status}")
                print(f"   Fields: Practice={opp.practice}, Geo={opp.geo}, Region={opp.region}, Sector={opp.sector}, Currency={opp.currency}")
                print("-" * 50)
    finally:
        db.close()

if __name__ == "__main__":
    check_db()
