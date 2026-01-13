import os
import sys
import json
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from oracle_service import get_from_oracle, ORACLE_BASE_URL, ORACLE_USER

def test_connection():
    print(f"📡 Testing Oracle CRM Connection...")
    print(f"Base URL: {ORACLE_BASE_URL}")
    print(f"User: {ORACLE_USER}")
    
    # Try fetching a small batch
    params = {"limit": 5, "onlyData": "true"}
    data = get_from_oracle("opportunities", params=params)
    
    if "error" in data:
        print(f"❌ API Error: {data['error']}")
        return

    items = data.get("items", [])
    print(f"✅ API Success! Fetched {len(items)} items.")
    
    if items:
        print("\nSample Item Keys:", list(items[0].keys()))
        print("Sample OptyNumber:", items[0].get("OptyNumber"))
    else:
        print("\n⚠️  The Oracle CRM returned 0 opportunities. This explains why your database is empty.")
        print("Full Response API Body:", json.dumps(data, indent=2))

if __name__ == "__main__":
    test_connection()
