
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")
USER = os.getenv("ORACLE_USER")
PASS = os.getenv("ORACLE_PASSWORD")

def explore():
    url = f"{BASE_URL}/crmRestApi/resources/latest/opportunities"
    print(f"📡 Testing URL: {url}")
    
    # Try 1: Bare fetch for the first item
    print("\n--- Try 1: Fetching FIRST available record ---")
    try:
        r = requests.get(url, auth=(USER, PASS), params={"limit": 1}, timeout=30)
        print(f"Status: {r.status_code}")
        if r.ok:
            data = r.json()
            items = data.get('items', [])
            if items:
                print("✅ Found a record!")
                keys = sorted(items[0].keys())
                print(f"Keys found ({len(keys)}):")
                for k in keys:
                    print(f"  - {k}")
                return
            else:
                print("ℹ️ No items found in item-list.")
        else:
            print(f"❌ Error: {r.text[:200]}")
    except Exception as e:
        print(f"❌ Connection error: {e}")

    # Try 2: Searching specifically for your ID 1602737
    print("\n--- Try 2: Fetching specifically ID 1602737 ---")
    try:
        # We try q search
        r = requests.get(url, auth=(USER, PASS), params={"q": "OptyNumber='1602737'"}, timeout=30)
        if r.ok:
            items = r.json().get('items', [])
            if items:
                print("✅ Found Opportunity 1602737!")
                keys = sorted(items[0].keys())
                for k in keys:
                    print(f"  - {k}")
                return
            else:
                print("ℹ️ ID 1602737 not found via query.")
        
        # Try direct link
        url_direct = f"{url}/1602737"
        print(f"📡 Testing direct URL: {url_direct}")
        r = requests.get(url_direct, auth=(USER, PASS), timeout=30)
        if r.ok:
            print("✅ Found Opportunity 1602737 via Direct Link!")
            item = r.json()
            keys = sorted(item.keys())
            for k in keys:
                print(f"  - {k}")
        else:
            print(f"❌ Direct link failed: {r.status_code}")
            
    except Exception as e:
        print(f"❌ Error in targeted search: {e}")

if __name__ == "__main__":
    explore()
