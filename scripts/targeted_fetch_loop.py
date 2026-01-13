
import os
import sys
import httpx
from datetime import datetime
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Add project root and backend to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if "scripts" in BASE_DIR:
    BASE_DIR = os.path.dirname(BASE_DIR)

sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'backend'))

load_dotenv(os.path.join(BASE_DIR, '.env'))

try:
    from backend.database import SessionLocal, Opportunity, OpportunityDetails, init_db
    from backend.oracle_service import map_oracle_to_db, get_auth_header
except ImportError as e:
    print(f"❌ ImportError: {e}")
    sys.exit(1)

# Combined List of Targets
TARGET_IDS = [
    "1602737", "1602738", "1693827", "1658743", "1658758", 
    "1657755", "1744044", "1754130", "1759271", "1755209", "1733846"
]

ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")

def fetch_bulk_and_store():
    print(f"🚀 Starting Bulk IN-Clause Sync")
    
    init_db()
    db: Session = SessionLocal()
    auth_header = get_auth_header()
    
    # Construct the IN clause string: '1','2','3'
    id_list_str = ",".join([f"'{tid}'" for tid in TARGET_IDS])
    
    # Query: RecordSet='ALL';OptyNumber in ('1602737'...)
    q_val = f"RecordSet='ALL';OptyNumber in ({id_list_str})"
    
    # Fields to fetch (Dashboard Visible fields + Essential IDs)
    fields = (
        "OptyId,OptyNumber,Name,Revenue,CurrencyCode,WinProb,"
        "SalesStage,SalesMethod,OwnerName,AccountName,"
        "Practice_c,Geo_c,Region_c,BusinessUnit_c,"
        "CloseDate,LastUpdateDate,Description"
        # Add any other specific custom fields visible on dashboard here
    )
    
    params = {
        "q": q_val,
        "onlyData": "true",
        "limit": 50,  # Single batch for 11 records
        "fields": fields
    }
    
    url = f"{ORACLE_BASE_URL}/crmRestApi/resources/latest/opportunities"
    
    print(f"📡 Requesting Bulk Data (Count: {len(TARGET_IDS)})...")
    
    with httpx.Client(headers=auth_header, timeout=60.0) as client:
        try:
            response = client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                print(f"✅ Success! Received {len(items)} items.")
                
                for item in items:
                    print(f"   🔹 Processing: {item.get('OptyNumber')} - {item.get('Name')}")
                    
                    mapped = map_oracle_to_db(item)
                    if mapped:
                        primary_data = mapped["primary"]
                        details_data = mapped["details"]
                        
                        existing = db.query(Opportunity).filter(Opportunity.remote_id == primary_data['remote_id']).first()
                        if existing:
                            for k, v in primary_data.items(): setattr(existing, k, v)
                        else:
                            db.add(Opportunity(**primary_data, workflow_status='NEW_FROM_CRM'))
                        
                        existing_details = db.query(OpportunityDetails).filter(OpportunityDetails.opty_number == primary_data['remote_id']).first()
                        if existing_details:
                            for k, v in details_data.items(): setattr(existing_details, k, v)
                        else:
                            db.add(OpportunityDetails(**details_data))
                
                db.commit()
                print("🏁 Bulk Sync Saved to Database.")
                
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"   Body: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    fetch_bulk_and_store()
