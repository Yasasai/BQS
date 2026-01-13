
import os
import sys
import httpx
from dotenv import load_dotenv

# Add project root and backend to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if "scripts" in BASE_DIR: BASE_DIR = os.path.dirname(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'backend'))

from oracle_service import get_auth_header
load_dotenv(os.path.join(BASE_DIR, '.env'))

auth = get_auth_header()
base_url = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")
target_id = "1602737"

print(f"--- DIAGNOSTIC RUN ---")

# TEST 1: Direct Path (User's request)
url_direct = f"{base_url}/crmRestApi/resources/latest/opportunities/{target_id}"
print(f"TEST 1: Direct GET {url_direct}")
with httpx.Client(headers=auth) as client:
    r1 = client.get(url_direct)
    print(f"Result: {r1.status_code}")
    if r1.status_code != 200:
        print(f"Error Body: {r1.text[:200]}")

# TEST 2: Search Query (Proper way for OptyNumber)
url_search = f"{base_url}/crmRestApi/resources/latest/opportunities"
params = {"q": f"RecordSet='ALL';OptyNumber='{target_id}'", "onlyData": "true"}
print(f"\nTEST 2: Search GET {url_search} with q=OptyNumber='{target_id}'")
with httpx.Client(headers=auth) as client:
    r2 = client.get(url_search, params=params)
    print(f"Result: {r2.status_code}")
    if r2.status_code == 200:
        items = r2.json().get('items', [])
        print(f"Items found: {len(items)}")
        if items:
            print(f"ID retrieved: {items[0].get('OptyNumber')} - {items[0].get('Name')}")
    else:
        print(f"Error Body: {r2.text[:200]}")
