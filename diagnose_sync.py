import os
import sys
import json
import logging

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from oracle_service import get_from_oracle, map_oracle_to_db
from database import SessionLocal, Opportunity, OpportunityDetails, SyncLog, init_db

logging.basicConfig(level=logging.INFO)

def diagnose():
    print("🛠️  SYNC DIAGNOSTICS")
    print("1. Initializing Database (Self-Healing)...")
    init_db()
    
    print("\n2. Fetching Raw Data from Oracle CRM...")
    # Try with 'latest'
    data = get_from_oracle("opportunities", params={"limit": 1, "onlyData": "true"})
    
    if "error" in data:
        print(f"❌ API Error: {data['error']}")
        # Try with the version from screenshot as fallback
        print("🔄 Retrying with specific API version 11.13.18.05...")
        # Check if we can override the base url for one call
        from oracle_service import ORACLE_BASE_URL, ORACLE_USER, ORACLE_PASS
        import requests
        from requests.auth import HTTPBasicAuth
        url = f"{ORACLE_BASE_URL}/crmRestApi/resources/11.13.18.05/opportunities"
        try:
            r = requests.get(url, auth=HTTPBasicAuth(ORACLE_USER, ORACLE_PASS), params={"limit": 1, "onlyData": "true"}, timeout=30)
            print(f"   Status Code: {r.status_code}")
            data = r.json()
        except Exception as e:
            print(f"   Fallback failed: {e}")
            return

    items = data.get("items", [])
    print(f"✅ Fetched {len(items)} items from Oracle.")
    
    if not items:
        print("⚠️  Oracle returned 0 items. Possible reasons:")
        print("   - The user has no opportunities assigned.")
        print("   - The 'opportunities' resource is restricted.")
        print("   - Use 'opportunity' (singular) or 'OptyResource' if 'opportunities' is empty.")
        return

    item = items[0]
    print(f"🔍 First Item (Keys): {list(item.keys())[:10]}...")
    print(f"🔍 OptyNumber: {item.get('OptyNumber')}")

    print("\n3. Testing Mapping...")
    mapped = map_oracle_to_db(item)
    if not mapped:
        print("❌ Mapping failed! Check oracle_service.py map_oracle_to_db.")
        return
    print("✅ Mapping Success!")
    print(f"   Primary Name: {mapped['primary']['name']}")
    print(f"   Detail Description: {str(mapped['details']['description'])[:50]}...")
    print(f"   Detail Raw JSON present: {'raw_json' in mapped['details']}")

    print("\n4. Testing DB Save...")
    db = SessionLocal()
    try:
        from sync_manager import SyncManager
        manager = SyncManager()
        manager.db = db
        # Use dummy sync id
        manager.sync_batch([item], 0)
        print("✅ DB Save Success!")
        
        count = db.query(OpportunityDetails).count()
        print(f"Total records in OpportunityDetails: {count}")
    except Exception as e:
        print(f"❌ DB Save Failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    diagnose()
