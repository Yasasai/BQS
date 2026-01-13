
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

BASE_URL = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")
USER = os.getenv("ORACLE_USER")
PASS = os.getenv("ORACLE_PASSWORD")

def test_variations():
    variations = [
        # 1. Bare fetch (No params)
        {"name": "Bare Fetch", "url": f"{BASE_URL}/crmRestApi/resources/latest/opportunities", "params": {}},
        
        # 2. Only limit
        {"name": "Limit Only", "url": f"{BASE_URL}/crmRestApi/resources/latest/opportunities", "params": {"limit": 5}},
        
        # 3. Search for the user's specific ID as a query
        {"name": "Query Specific ID", "url": f"{BASE_URL}/crmRestApi/resources/latest/opportunities", "params": {"q": "OptyNumber='1602737'"}},
        
        # 4. Check internal health/metadata
        {"name": "Describe Metadata", "url": f"{BASE_URL}/crmRestApi/resources/latest/opportunities/describe", "params": {}},
    ]
    
    for v in variations:
        print(f"\n--- Testing: {v['name']} ---")
        print(f"URL: {v['url']}")
        try:
            response = requests.get(v['url'], auth=(USER, PASS), params=v['params'], timeout=20)
            print(f"Status: {response.status_code}")
            if response.ok:
                data = response.json()
                items = data.get('items', [])
                print(f"Items found: {len(items)}")
                if items:
                    print(f"First item name: {items[0].get('Name')}")
                elif 'count' in data:
                    print(f"Total count reported: {data.get('count')}")
                
                # If it's a 404 on the specific ID query, it might be the wrong endpoint
            else:
                print(f"Error Body: {response.text[:200]}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    test_variations()
