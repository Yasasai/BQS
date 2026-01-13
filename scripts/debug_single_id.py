
import os
import sys
import httpx
from dotenv import load_dotenv

load_dotenv()

headers = {
    "Authorization": "Basic " + os.getenv("ORACLE_PASS_ENCODED", "base64_here"), # I'll use the helper instead
}

# Use the helper to be safe
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if "scripts" in BASE_DIR: BASE_DIR = os.path.dirname(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'backend'))
from oracle_service import get_auth_header

auth = get_auth_header()
base_url = os.getenv("ORACLE_BASE_URL")
target_id = "1602737"

print(f"DEBUG: Testing ID {target_id} on {base_url}")
url = f"{base_url}/crmRestApi/resources/latest/opportunities"
params = {"q": f"RecordSet='ALL';OptyNumber='{target_id}'", "onlyData": "true"}

with httpx.Client(headers=auth) as client:
    resp = client.get(url, params=params)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        items = resp.json().get('items', [])
        if items:
            print("SUCCESS! Data found:")
            item = items[0]
            for k in ['OptyNumber', 'Name', 'Revenue', 'StatusCode', 'SalesStage']:
                print(f"  {k}: {item.get(k)}")
        else:
            print("FAILED: No items found in search.")
    else:
        print(f"FAILED: {resp.text}")
