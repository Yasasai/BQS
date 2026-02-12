
import os
import sys
import httpx
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Setup Logging
LOG_FILE = "fetch_1602736.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(message)s')

def log(msg):
    print(msg)
    logging.info(msg)

# Path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if "scripts" in BASE_DIR:
    BASE_DIR = os.path.dirname(BASE_DIR)
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'backend'))

log("DEBUG: Script initialized.")
log(f"DEBUG: Base Dir: {BASE_DIR}")

# Load credentials
load_dotenv(os.path.join(BASE_DIR, '.env'))

try:
    from backend.database import SessionLocal, Opportunity, OpportunityDetails, init_db
    from backend.oracle_service import map_oracle_to_db, get_auth_header
    log("DEBUG: Imports successful.")
except ImportError as e:
    log(f"❌ ImportError: {e}")
    sys.exit(1)

OPTY_ID = "1602736"
ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")
URL = f"{ORACLE_BASE_URL}/crmRestApi/resources/latest/opportunities/{OPTY_ID}"

def fetch_single_direct():
    log(f"🚀 Fetching Single ID: {OPTY_ID}")
    log(f"🔗 URL: {URL}")
    
    try:
        init_db()
        db: Session = SessionLocal()
        auth_header = get_auth_header()
        
        if not auth_header:
            log("❌ No Auth Header generated")
            return

        with httpx.Client(headers=auth_header, timeout=60.0) as client:
            log(f"📡 Sending GET request...")
            response = client.get(URL)
            log(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                log(f"✅ Data Received: {data.get('Name')}")
                
                # Map and Save
                mapped = map_oracle_to_db(data)
                if mapped:
                    primary_data = mapped["primary"]
                    details_data = mapped["details"]
                    
                    # Upsert Primary
                    existing = db.query(Opportunity).filter(Opportunity.remote_id == str(OPTY_ID)).first()
                    if existing:
                        for k, v in primary_data.items(): setattr(existing, k, v)
                        log("   🔹 Updated existing Opportunity record.")
                    else:
                        db.add(Opportunity(**primary_data, workflow_status='NEW_FROM_CRM'))
                        log("   🔹 Created NEW Opportunity record.")
                    
                    # Upsert Details
                    existing_details = db.query(OpportunityDetails).filter(OpportunityDetails.opty_number == str(OPTY_ID)).first()
                    if existing_details:
                        for k, v in details_data.items(): setattr(existing_details, k, v)
                        log("   🔹 Updated existing Details record.")
                    else:
                        db.add(OpportunityDetails(**details_data))
                        log("   🔹 Created NEW Details record.")
                    
                    db.commit()
                    log("🏁 Successfully saved to PostgreSQL.")
                else:
                    log("❌ Mapping failed.")
            else:
                log(f"❌ Request failed: {response.text[:200]}")
                
    except Exception as e:
        log(f"❌ Exception: {e}")
        import traceback
        log(traceback.format_exc())

if __name__ == "__main__":
    fetch_single_direct()


https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/latest/opportunities/1602737





- **Database**: PostgreSQL with SQLAlchemy ORM.

- **Integration**: `oracle_service.py` handles authentication and data mapping between Oracle's complex schema and the streamlined BQS domain model.



---



## 4. Key Capabilities & "Wow" Factors

- **Self-Healing Sync**: The system can rebuild its local dataset from Oracle at any time. If the Oracle API is down, it gracefully degrades to using the last known local data.

- **Visual Auditing**: Changes to scores are tracked. The history view allows auditors to see exactly who changed a score from 'High' to 'Low' and when.

- **One-Click Setup**: The entire environment can be spun up on a new machine using the `setup_project.py` and `run_app.bat` scripts, which handle everything from Python venv creation to database migration.



Can you tweak this a bit with this excel? 