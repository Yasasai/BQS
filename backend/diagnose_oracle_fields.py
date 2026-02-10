
import os
import sys
import requests
import json
import logging
from dotenv import load_dotenv

# Path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Configuration
ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL")
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def diagnose():
    if not ORACLE_BASE_URL:
        print("❌ ORACLE_BASE_URL not set.")
        return

    auth = requests.auth.HTTPBasicAuth(ORACLE_USER, ORACLE_PASSWORD)
    
    # 1. Inspect "Describe" to find exact field names
    print("\n🔍 --- 1. Fetching Field Description ---")
    desc_url = f"{ORACLE_BASE_URL}/crmRestApi/resources/11.12.1.0/opportunities/describe"
    try:
        resp = requests.get(desc_url, auth=auth, timeout=30)
        if resp.ok:
            data = resp.json()
            # print structure of describe
            # usually data['Resources']['opportunities']['attributes'] list
            # We want to check for 'Status', 'StatusCode', 'StatusCd', 'Revenue', 'Practice', etc.
            
            # This structure can vary, let's just dump keys or try to find specific ones
            print(f"✅ Describe Success. Keys: {list(data.keys())}")
            
            # Simple text search in response text for keywords
            text = resp.text
            for kw in ["StatusCode", "StatusCd", "OptyStatusCd", "Practice", "Revenue", "EffectiveDate", "GEO", "Geo", "Region"]:
                print(f"   Keyword '{kw}' found count: {text.count(kw)}")
        else:
            print(f"❌ Describe Failed: {resp.status_code} - {resp.text[:200]}")
    except Exception as e:
        print(f"❌ Describe Error: {e}")

    # 2. Test Minimum Working Request (No fields, limit 1)
    print("\n🔍 --- 2. Testing Minimum Working Request ---")
    min_url = f"{ORACLE_BASE_URL}/crmRestApi/resources/11.12.1.0/opportunities"
    params = {"limit": 1}
    try:
        resp = requests.get(min_url, params=params, auth=auth, timeout=30)
        if resp.ok:
            data = resp.json()
            items = data.get("items", [])
            print(f"✅ Min Request Success. Fetched {len(items)} items.")
            if items:
                print("   Sample Keys:", list(items[0].keys()))
                print("   Status-like fields:", {k:v for k,v in items[0].items() if 'tatus' in k})
                print("   Practice-like fields:", {k:v for k,v in items[0].items() if 'ractice' in k})
        else:
            print(f"❌ Min Request Failed: {resp.status_code} - {resp.text[:200]}")
    except Exception as e:
        print(f"❌ Min Request Error: {e}")

    # 3. Test Count Only (totalResults=true, limit=0 or 1)
    print("\n🔍 --- 3. Testing Count Only ---")
    count_params = {"totalResults": "true", "limit": 1, "fields": "OptyId"} 
    # User says totalResults cant mix with fields/limit... wait. 
    # User said: "Oracle does NOT allow totalResults=true together with fields, offset, limit"
    # So let's try pure count: ?totalResults=true (limit undefined) or just totalResults=true?
    # Actually usually ?q=...&totalResults=true
    
    try:
        # User recommended pattern: GET /opportunities?q=StatusCd='OPEN'&totalResults=true
        # We don't know StatusCd yet, lets try generic
        p = {"totalResults": "true", "limit": 1} 
        resp = requests.get(min_url, params=p, auth=auth, timeout=30)
        if resp.ok:
             print(f"✅ Count Request Success (with limit=1). Total: {resp.json().get('totalResults')}")
        else:
             print(f"❌ Count Request Failed (with limit=1): {resp.status_code}")
             
        # Try without limit
        p2 = {"totalResults": "true"}
        resp2 = requests.get(min_url, params=p2, auth=auth, timeout=30)
        if resp2.ok:
             print(f"✅ Count Request Success (no limit). Total: {resp2.json().get('totalResults')}")
        else:
             print(f"❌ Count Request Failed (no limit): {resp2.status_code}")

    except Exception as e:
        print(f"❌ Count Error: {e}")

if __name__ == "__main__":
    diagnose()
