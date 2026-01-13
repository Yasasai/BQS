import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from database import SessionLocal, Opportunity, OpportunityDetails, init_db

def check():
    print("Checking database...")
    db = SessionLocal()
    try:
        opp_count = db.query(Opportunity).count()
        det_count = db.query(OpportunityDetails).count()
        print(f"Opp Count: {opp_count}")
        print(f"Det Count: {det_count}")
        
        if opp_count > 0:
            opp = db.query(Opportunity).first()
            print(f"Sample Opp Description: {str(opp.description)[:30]}...")
            
        if det_count > 0:
            det = db.query(OpportunityDetails).first()
            print(f"Sample Det Description: {str(det.description)[:30]}...")
            print(f"Sample Det Raw JSON keys: {list(det.raw_json.keys())[:3] if det.raw_json else 'None'}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check()
