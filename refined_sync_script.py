import os
import sys
print("--- 🚀 Script Started 🚀 ---")
import logging
from datetime import datetime
# --- CONFIGURATION: Load from .env file ---
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

# Set environment variables (with fallback for local development)
os.environ["ORACLE_USER"] = os.getenv("ORACLE_USER", "")
os.environ["ORACLE_PASSWORD"] = os.getenv("ORACLE_PASSWORD", "")
os.environ["ORACLE_BASE_URL"] = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")

if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = os.getenv("DATABASE_URL", "postgresql://postgres:password@127.0.0.1:5432/bqs")

USERNAME = os.environ.get("ORACLE_USER")
PASSWORD = os.environ.get("ORACLE_PASSWORD")

if not USERNAME or not PASSWORD:
    print("❌ ERROR: ORACLE_USER and ORACLE_PASSWORD must be set in .env file")
    print("Create a .env file with:")
    print("ORACLE_USER=your_username")
    print("ORACLE_PASSWORD=your_password")
    sys.exit(1)

print(f"✅ Credentials loaded from .env (User: {USERNAME})")

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from oracle_service import (
    fetch_single_opportunity, 
    get_all_opportunities, 
    map_oracle_to_db,
    ORACLE_BASE_URL
)
from database import SessionLocal, Opportunity, OpportunityIDLog, init_db
from sync_manager import SyncManager

# Setup basic logging to see results systematically
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SystematicSync")

def run_tweaked_sync(target_opty=None):
    """
    Tweaked logic according to your plan:
    1. Interlinks Oracle Link/Creds automatically from .env
    2. Performs Self-Healing Migration on the Database
    3. Uses OptyNumber as the primary reference
    4. Self-heals if data is incomplete
    """
    # Trigger Universal Self-Healing Migration
    init_db()
    
    db = SessionLocal()
    manager = SyncManager()
    manager.db = db # Interlink the DB session
    
    print("\n" + "="*60)
    print("🚀 TARGETED SYSTEMATIC SYNC")
    print(f"📡 SOURCE: {ORACLE_BASE_URL}")
    print("="*60)

    try:
        # --- STEP 2: THE FETCH (Systematic & Light) ---
        if target_opty:
            print(f"\n[1/3] Fetching Reference ID: {target_opty}...")
            raw_items = [fetch_single_opportunity(target_opty)]
        else:
            print("\n[1/3] Fetching ALL systematic batches...")
            raw_gen = get_all_opportunities(batch_size=20)
            raw_items = []
            for batch in raw_gen:
                print(f"   -> Found batch of {len(batch)} records")
                raw_items.extend(batch)
            
            if not raw_items:
                print("⚠️  Warning: Oracle returned zero items. Check your .env credentials or if the user has records.")
        
        # --- STEP 3: THE SAVE (Interlinked & Self-Healing) ---
        print(f"\n[2/3] Processing {len(raw_items)} records into PostgreSQL...")
        
        # We use a dummy log_id for this manual trigger
        # In the full system, sync_manager creates this automatically
        dummy_sync_id = 999 

        for item in raw_items:
            if not item: continue
            
            # COORDINATE: Everything centered around OptyNumber
            opty_num = item.get('OptyNumber') or item.get('OptyId')
            print(f"   -> Reference: {opty_num}")
            print(f"   -> Raw Keys: {list(item.keys())}")
            
            # Map and Auto-Heal (Deep Fetch happens inside sync_batch if needed)
            # This is where the 'Selenium-style' data becomes 'Professional' data
            manager.sync_batch([item], dummy_sync_id)
            
        print(f"\n[3/3] Success! Checked OpportunityIDLog for systematic changes.")
        print("="*60)

    except Exception as e:
        print(f"❌ Critical Failure: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Perform a systematic sync of available opportunities
    # This will populate both 'opportunities' and 'opportunity_details' tables.
    run_tweaked_sync() 
