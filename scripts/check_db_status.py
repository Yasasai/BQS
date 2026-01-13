
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database import SessionLocal, Opportunity

def check_counts():
    db = SessionLocal()
    try:
        count = db.query(Opportunity).count()
        print(f"Total Opportunities in Database: {count}")
        
        latest = db.query(Opportunity).order_by(Opportunity.last_synced_at.desc()).first()
        if latest:
            print(f"Latest Sync Entry: {latest.name} (Synced at: {latest.last_synced_at})")
    finally:
        db.close()

if __name__ == "__main__":
    check_counts()
