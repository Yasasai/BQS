
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

BASE_URL = os.getenv("ORACLE_BASE_URL")
USER = os.getenv("ORACLE_USER")
PASS = os.getenv("ORACLE_PASSWORD")

def discover_fields():
    # Fetch a single record with ALL fields to see what's available
    url = f"{BASE_URL}/crmRestApi/resources/latest/opportunities"
    params = {"limit": 1}
    
    print(f"Connecting to: {url}")
    response = requests.get(url, auth=(USER, PASS), params=params)
    
    if response.ok:
        items = response.json().get('items', [])
        if items:
            print("\n✅ Found Opportunity. Available fields:")
            keys = sorted(items[0].keys())
            for k in keys:
                print(f"  - {k}")
            
            # Specifically check for common synonyms
            print("\nSearching for custom fields (ending in _c):")
            custom = [k for k in keys if k.endswith('_c')]
            for c in custom:
                print(f"  - {c}")
        else:
            print("❌ No opportunities found in CRM.")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    discover_fields()
