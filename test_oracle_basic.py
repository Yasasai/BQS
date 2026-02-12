
import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

load_dotenv()

ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL")
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")

print(f"Connecting to: {ORACLE_BASE_URL}")
print(f"User: {ORACLE_USER}")

url = f"{ORACLE_BASE_URL}/crmRestApi/resources/11.12.1.0/opportunities?limit=1"
try:
    response = requests.get(url, auth=HTTPBasicAuth(ORACLE_USER, ORACLE_PASSWORD), timeout=30)
    print(f"Status Code: {response.status_code}")
    if response.ok:
        print("Success! Connection established.")
        data = response.json()
        items = data.get("items", [])
        print(f"Items found: {len(items)}")
        if items:
            print(f"First Opportunity: {items[0].get('Name')}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
