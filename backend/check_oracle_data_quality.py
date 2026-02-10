
import os
import sys
import logging
import requests
import json
from dotenv import load_dotenv

# Path setup to include backend modules
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Configuration
ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL")
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", os.getenv("ORACLE_PASS"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_data_quality():
    if not ORACLE_BASE_URL:
        print("❌ ORACLE_BASE_URL not set.")
        return

    print(f"📡 Connecting to: {ORACLE_BASE_URL}")
    url = f"{ORACLE_BASE_URL}/crmRestApi/resources/11.12.1.0/opportunities"
    
    # We fetch specifically 5 items to check structure
    params = {
        "q": "StatusCode='OPEN'", # Using the same query as async_sync.py
        "limit": 5,
        "totalResults": "true"
    }
    
    auth = requests.auth.HTTPBasicAuth(ORACLE_USER, ORACLE_PASSWORD)
    
    try:
        resp = requests.get(url, params=params, auth=auth, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        items = data.get("items", [])
        print(f"✅ Connection Successful. Status: {resp.status_code}")
        print(f"📊 Total Results (as reported by Oracle): {data.get('totalResults')}")
        print(f"📦 Fetched {len(items)} sample items.")
        
        if items:
            sample = items[0]
            print("\n🔍 --- SAMPLE DATA STRUCTURE (First Item) ---")
            print(json.dumps(sample, indent=2))
            
            # Verify Key Fields for Mapping
            print("\n🛠️ --- MAPPING VERIFICATION ---")
            print(f"OptyId: {sample.get('OptyId')} (Expected: Not None)")
            print(f"OptyNumber: {sample.get('OptyNumber')} (Expected: Not None)")
            print(f"Name: {sample.get('Name')}")
            print(f"TargetPartyName: {sample.get('TargetPartyName')}")
            print(f"Revenue: {sample.get('Revenue')}")
            print(f"Practice_c: {sample.get('Practice_c')} (Critical for Assignment)")
            print(f"SalesStage: {sample.get('SalesStage')}")
            print(f"LastUpdateDate: {sample.get('LastUpdateDate')}")
            
            # Check for fields that might be missing or named differently
            missing_keys = [k for k in ["OptyId", "OptyNumber", "Name", "Revenue"] if k not in sample]
            if missing_keys:
                print(f"❌ MISSING CRITICAL KEYS: {missing_keys}")
            else:
                print("✅ Critical keys present.")
                
            if "Practice_c" not in sample:
                 print("⚠️ WARNING: 'Practice_c' not found. Check custom field name.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_data_quality()
