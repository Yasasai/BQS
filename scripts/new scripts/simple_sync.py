import os
import sys
import httpx
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# --- 1. SETUP & CONFIG ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if "scripts" in BASE_DIR: BASE_DIR = os.path.dirname(BASE_DIR)
sys.path.append(BASE_DIR)

# Load Environment Variables
# Try loading from backend/.env if simple_sync is in root
env_path = os.path.join(BASE_DIR, 'backend', '.env')
if not os.path.exists(env_path):
    env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(env_path)

ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", os.getenv("ORACLE_PASS"))

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
def log(msg): 
    print(msg, flush=True)
    logging.info(msg)

# ...

if __name__ == "__main__":
    print("Beginning execution of simple_sync.py...", flush=True)
    fetch_and_store_immediately()
try:
    from backend.database import SessionLocal, Opportunity, OpportunityDetails, init_db
    # from backend.oracle_service import get_auth_header # Not strictly needed if we use simple auth
except ImportError as e:
    log(f"❌ Critical: Could not import backend modules. Error: {e}")
    # Fallback for when running directly inside backend/
    try:
        sys.path.append(os.path.join(BASE_DIR, 'backend'))
        from database import SessionLocal, Opportunity, OpportunityDetails, init_db
        log("✅ Configured fallback imports for running inside backend dir")
    except ImportError as e2:
        log(f"❌ Critical: Fallback failed too: {e2}")
        sys.exit(1)

# --- 2. THE MISSING MAPPING FUNCTION ---
def map_oracle_to_db(item):
    """
    Transforms Oracle JSON keys to your PostgreSQL Database columns.
    """
    try:
        # Extract fields safely (Handle missing data with .get)
        primary = {
            "remote_id": str(item.get("OptyId")),
            "name": item.get("Name"),
            "status": item.get("SalesStage"),
            "currency": item.get("CurrencyCode", "USD"),
            "deal_value": float(item.get("Revenue") or 0),  # 'Revenue' mapped to deal_value per existing model
            "close_date": None 
        }
        
        # Parse Date safely
        if item.get("EffectiveDate"):
            try:
                primary["close_date"] = datetime.strptime(item["EffectiveDate"][:10], "%Y-%m-%d")
            except: pass

        details = {
            "opty_number": str(item.get("OptyId")),
            "win_probability": float(item.get("WinProb") or 0),
            # "sales_method": item.get("SalesMethod"), # Check if this field exists in DB model
            # "target_party_id": str(item.get("TargetPartyId")) # Check if exist
        }
        
        # Add extra fields that usually exist in details based on known schema to prevent errors
        # (Assuming OpportunityDetails has these columns from previous files)
        
        return {"primary": primary, "details": details}
    except Exception as e:
        log(f"⚠️ Mapping Error for ID {item.get('OptyId')}: {e}")
        return None

# --- 3. THE INCREMENTAL SYNC LOGIC ---
def fetch_and_store_immediately():
    log("🚀 Starting Smart Incremental Sync...")
    
    init_db()
    db: Session = SessionLocal()
    
    # 1. Check last sync time
    try:
        # We query the max LastUpdateDate from OpportunityDetails as it tracks Oracle's state closely
        stmt = text("SELECT MAX(last_update_date) FROM opportunity_details")
        result = db.execute(stmt).fetchone()
        last_sync_date = result[0] if result and result[0] else None
        
        if last_sync_date:
            log(f"📅 Incremental Mode: Fetching changes since {last_sync_date}")
        else:
            log("📅 Full Sync Mode: No previous data found (or forcing full sync).")
            # Default to a safe past date or fetch all
            # last_sync_date = datetime(2023, 1, 1) 
    
    except Exception as e:
        log(f"⚠️ Could not determining last sync date: {e}. Defaulting to full fetch.")
        last_sync_date = None

    # API Configuration
    endpoint = f"{ORACLE_BASE_URL}/crmRestApi/resources/latest/opportunities"
    fields = "OptyId,Name,SalesStage,Revenue,CurrencyCode,WinProb,TargetPartyId,EffectiveDate,LastUpdateDate"
    
    limit = 10 
    offset = 0
    total_saved = 0
    
    with httpx.Client(auth=(ORACLE_USER, ORACLE_PASSWORD), timeout=60.0) as client:
        while True:
            # Construct Query
            base_q = "RecordSet='ALL'"
            if last_sync_date:
                # Oracle Format: YYYY-MM-DDTHH:MM:SS
                fmt_date = last_sync_date.strftime("%Y-%m-%dT%H:%M:%S")
                # Add buffer of 1 second to avoid duplicates if strictly >
                query_str = f"{base_q};LastUpdateDate > '{fmt_date}'"
            else:
                query_str = base_q
            
            log(f"📡 API Query: {query_str} | Offset: {offset}")

            params={
                "offset": offset, 
                "limit": limit, 
                "onlyData": "true",
                "q": query_str,
                "orderBy": "LastUpdateDate:asc", # Critical: Oldest changes first, so we resume correctly
                "fields": fields
            }

            response = client.get(endpoint, params=params)

            # Retry logic for 400 Bad Request (Field mismatch)
            if response.status_code == 400:
                log("⚠️  Field list invalid (400). Retrying without specific fields...")
                del params["fields"]
                response = client.get(endpoint, params=params)

            if response.status_code != 200:
                log(f"❌ API Error: {response.status_code} - {response.text}")
                break

            data = response.json()
            items = data.get("items", [])

            if not items:
                log("✅ No new items found. Sync is up-to-date.")
                break

            items_count = len(items)
            log(f"   Fetched {items_count} items (Limit: {limit}).")

            # --- PROCESS ROW BY ROW ---
            for item in items:
                mapped = map_oracle_to_db(item)
                if not mapped: continue

                try:
                    # 1. UPSERT OPPORTUNITY (Primary Table)
                    p_data = mapped["primary"]
                    
                    # Update or Insert
                    existing_opty = db.query(Opportunity).filter(Opportunity.remote_id == p_data["remote_id"]).first()
                    if existing_opty:
                        for k, v in p_data.items(): setattr(existing_opty, k, v)
                    else:
                        db.add(Opportunity(**p_data, workflow_status='NEW', status='New from CRM'))

                    # 2. UPSERT DETAILS (Details Table)
                    d_data = mapped["details"]
                    # Important: Parse LastUpdateDate for next sync marker
                    try:
                        oracle_update_str = item.get("LastUpdateDate")
                        if oracle_update_str:
                             # 2024-01-14T10:00:00+00:00 -> Remove Z or offset
                             d_data["last_update_date"] = datetime.fromisoformat(oracle_update_str.replace('Z', '+00:00'))
                    except: pass

                    opty_num = d_data["opty_number"]
                    existing_details = db.query(OpportunityDetails).filter(OpportunityDetails.opty_number == opty_num).first()
                    
                    if existing_details:
                        for k, v in d_data.items(): setattr(existing_details, k, v)
                    else:
                        db.add(OpportunityDetails(**d_data))

                    # 3. COMMIT IMMEDIATELY
                    db.commit()
                    total_saved += 1

                except Exception as e:
                    db.rollback()
                    log(f"❌ DB Error: {e}")
            
            log(f"✅ Committed batch. Total saved this run: {total_saved}")

            if not data.get("hasMore", False):
                break
            
            offset += limit
            
    log(f"\n🎉 Sync Session Complete. Processed {total_saved} records.")
    db.close()

if __name__ == "__main__":
    from sqlalchemy import text # Ensure import for the query
    fetch_and_store_immediately()
