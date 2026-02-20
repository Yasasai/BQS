
import requests
import os
import base64
import json
from dotenv import load_dotenv

# Load env - adjust path if not running from project root
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path=env_path)

ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASS = os.getenv("ORACLE_PASS")

def get_auth_header():
    if ORACLE_USER and ORACLE_PASS:
        auth_str = f"{ORACLE_USER}:{ORACLE_PASS}"
        encoded_auth = base64.b64encode(auth_str.encode()).decode()
        return {"Authorization": f"Basic {encoded_auth}"}
    return {}

def probe_endpoint(endpoint):
    url = f"{ORACLE_BASE_URL}/crmRestApi/resources/latest/{endpoint}"
    headers = get_auth_header()
    headers['Content-Type'] = 'application/json'
    
    print(f"GET {url}")
    try:
        response = requests.get(url, headers=headers, params={"limit": 1, "onlyData": "true"}, timeout=30)
        print(f"Status: {response.status_code}")
        if response.ok:
            data = response.json()
            items = data.get('items', [])
            if items:
                print(f"Found {len(items)} items. First item keys:")
                print(list(items[0].keys()))
                print("\nContent of first item:")
                print(json.dumps(items[0], indent=2))
            else:
                print("No items found.")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    endpoints_to_try = [
        "resources",
        "employees", # HR endpoint usually under hcmRestApi but worth a check here
        "users"      # Some old APIs use users
    ]
    
    for ep in endpoints_to_try:
        print(f"\n--- Probing {ep} ---")
        probe_endpoint(ep)
