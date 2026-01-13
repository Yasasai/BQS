
import os
import requests
from dotenv import load_dotenv
load_dotenv()

USER = os.getenv("ORACLE_USER")
PASS = os.getenv("ORACLE_PASSWORD")
BASE = os.getenv("ORACLE_BASE_URL")

def check_all_variants():
    url = f"{BASE}/crmRestApi/resources/latest/opportunities"
    variants = ["ALL", "ORG", "TEAM", "MGR"]
    
    print(f"DEBUG: Searching for Opportunity 1602737 using different RecordSets")
    
    for v in variants:
        print(f"\n--- Testing RecordSet='{v}' ---")
        q = f"RecordSet='{v}';OptyNumber='1602737'"
        try:
            r = requests.get(url, auth=(USER, PASS), params={"q": q, "limit": 1}, timeout=20)
            print(f"Status: {r.status_code}")
            if r.ok:
                items = r.json().get('items', [])
                if items:
                    print(f"✅ FOUND with RecordSet={v}")
                    return
                else:
                    print(f"❌ Not found with RecordSet={v}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_all_variants()
