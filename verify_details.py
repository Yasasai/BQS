import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from database import DATABASE_URL, OpportunityDetails, init_db

def verify_data():
    # Force schema sync before verification
    init_db()
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        count = db.query(OpportunityDetails).count()
        print(f"Total records in OpportunityDetails: {count}")
        
        if count > 0:
            latest = db.query(OpportunityDetails).order_by(OpportunityDetails.last_synced_at.desc()).first()
            print("\n--- LATEST SYNCED OPPORTUNITY DETAILS ---")
            print(f"Opty Number: {latest.opty_number}")
            print(f"Name       : {latest.name}")
            print(f"Account    : {latest.account_name}")
            print(f"Practice   : {latest.practice}")
            print(f"Revenue    : {latest.revenue} {latest.currency_code}")
            print(f"Owner      : {latest.owner_name}")
            print(f"Contact    : {latest.primary_contact}")
            print(f"Stage      : {latest.sales_stage}")
            print(f"Effective  : {latest.effective_date}")
            print(f"Last Update: {latest.last_update_date}")
            print(f"Synced At  : {latest.last_synced_at}")
            print(f"Description: {(latest.description[:50] + '...') if latest.description else 'None'}")
            print(f"Raw JSON   : {'✅ Present' if latest.raw_json else '❌ Missing'}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_data()
