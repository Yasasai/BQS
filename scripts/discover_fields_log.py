
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

BASE_URL = os.getenv("ORACLE_BASE_URL")
USER = os.getenv("ORACLE_USER")
PASS = os.getenv("ORACLE_PASSWORD")

def discover_fields():
    url = f"{BASE_URL}/crmRestApi/resources/latest/opportunities"
    params = {"limit": 1}
    
    with open("fields_discovery.log", "w") as f:
        f.write(f"Connecting to: {url}\n")
        try:
            response = requests.get(url, auth=(USER, PASS), params=params, timeout=30)
            if response.ok:
                items = response.json().get('items', [])
                if items:
                    f.write("✅ Found Opportunity. Available fields:\n")
                    keys = sorted(items[0].keys())
                    for k in keys:
                        f.write(f"  - {k}\n")
                else:
                    f.write("❌ No opportunities found.\n")
            else:
                f.write(f"❌ Failed: {response.status_code}\n")
                f.write(response.text)
        except Exception as e:
            f.write(f"❌ Error: {str(e)}\n")

if __name__ == "__main__":
    discover_fields()
