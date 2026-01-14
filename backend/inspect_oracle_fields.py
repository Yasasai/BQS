
import os
import requests
import base64
import json
import sys
from dotenv import load_dotenv

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

print("--- DIAGNOSTIC SCRIPT STARTING ---")

# Load env
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path=env_path)

BASE_URL = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")
USER = os.getenv("ORACLE_USER")
PASS = os.getenv("ORACLE_PASSWORD", os.getenv("ORACLE_PASS"))

print(f"Target: {BASE_URL}")
print(f"User: {USER}")

if not USER or not PASS:
    print("❌ CREDENTIALS MISSING IN .ENV")
    sys.exit(1)

url = f"{BASE_URL}/crmRestApi/resources/latest/opportunities/describe"

try:
    print(f"Sending GET request to {url}...")
    auth = (USER, PASS)
    resp = requests.get(url, auth=auth, timeout=60)
    
    print(f"Response Code: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        if "attributes" in data:
            fields = [item['name'] for item in data['attributes']]
            print(f"✅ Found {len(fields)} fields.")
            
            with open("oracle_fields_dump.txt", "w") as f:
                f.write("\n".join(sorted(fields)))
            print("Saved to oracle_fields_dump.txt")
            
            # Print important ones
            interest = ["Revenue", "Practice", "Geo", "Region", "Sector", "Deal", "Estimated"]
            print("\nSpeculuative Matches:")
            for i in interest:
                matches = [f for f in fields if i.lower() in f.lower()]
                print(f" - {i}: {matches}")
        else:
            print("❌ No 'attributes' in response json")
    else:
        print(f"❌ Error: {resp.text[:500]}")

except Exception as e:
    print(f"❌ Exception: {e}")
