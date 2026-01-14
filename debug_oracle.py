
import os
import httpx
from dotenv import load_dotenv

# 1. Load Credentials
load_dotenv()
BASE_URL = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")
USER = os.getenv("ORACLE_USER")
# Fallback to ORACLE_PASS if ORACLE_PASSWORD is not set, just in case
PWD = os.getenv("ORACLE_PASSWORD") or os.getenv("ORACLE_PASS")

def test_connection():
    print(f"📡 Testing connection to: {BASE_URL}")
    print(f"👤 User: {USER}")

    # 2. THE SIMPLIFIED URL (Crucial!)
    # We removed 'fields', 'onlyData', 'orderBy', and 'limit' to see if a PLAIN request works.
    url = f"{BASE_URL}/crmRestApi/resources/latest/opportunities"

    try:
        # Use simple auth tuple
        response = httpx.get(url, auth=(USER, PWD), timeout=30)
        
        print(f"\nStatus Code: {response.status_code}")
        
        # 3. PRINT THE RAW TRUTH
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            print(f"✅ Success! Found {len(items)} items.")
            
            if len(items) > 0:
                print("First item sample:", items[0].get('Name'))
                print("Keys available:", list(items[0].keys()))
            else:
                print("⚠️ The request succeeded, but the list is EMPTY.")
                print("Possible Cause: User has no permissions to view data.")
        else:
            print("❌ Error Response:", response.text)

    except Exception as e:
        print(f"💥 Crash: {e}")

if __name__ == "__main__":
    test_connection()
