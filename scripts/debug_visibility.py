
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

BASE_URL = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")
USER = os.getenv("ORACLE_USER")
PASS = os.getenv("ORACLE_PASSWORD")

def test_visibility():
    endpoint = f"{BASE_URL}/crmRestApi/resources/latest/opportunities"
    
    print(f"DEBUG: Testing visibility for Opportunity 1602737 (from screenshot)")
    
    attempts = [
        # 1. Standard Query
        {"name": "Standard Query", "params": {"q": "OptyNumber='1602737'", "onlyData": "true"}},
        
        # 2. RecordSet=ALL (Common for Oracle Sales Cloud to see beyond 'My' records)
        {"name": "RecordSet ALL", "params": {"q": "RecordSet='ALL';OptyNumber='1602737'", "onlyData": "true"}},
        
        # 3. Finder approach (Used to mimic UI saved searches)
        {"name": "All Opportunities Finder", "params": {"finder": "AllOpportunitiesFinder", "onlyData": "true", "limit": 5}},
        
        # 4. Search by Name instead (Copy-pasted from your screenshot)
        {"name": "Search by Name", "params": {"q": "Name LIKE '1569344 IAM%'", "onlyData": "true"}},

        # 5. Check if using OptyId instead of OptyNumber works
        {"name": "OptyId Search", "params": {"q": "OptyId='1602737'", "onlyData": "true"}},
    ]
    
    for a in attempts:
        print(f"\n--- Attempt: {a['name']} ---")
        try:
            r = requests.get(endpoint, auth=(USER, PASS), params=a['params'], timeout=30)
            print(f"Status: {r.status_code}")
            if r.ok:
                items = r.json().get('items', [])
                print(f"Success! Items found: {len(items)}")
                if items:
                    print(f"Data Sample: {json.dumps(items[0], indent=2)[:500]}...")
            else:
                print(f"Failure: {r.text[:300]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_visibility()
