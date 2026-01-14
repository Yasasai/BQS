import requests
from requests.auth import HTTPBasicAuth
import json

# Test Oracle API with different endpoints
ORACLE_USER = "yasasvi.upadrasta@inspiraenterprise.com"
ORACLE_PASS = "Welcome@123"
BASE_URL = "https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources"

print("🔍 Testing Oracle API Permissions...\n")

# Test 1: Check if we can access the API at all
print("Test 1: Basic API Access")
url = f"{BASE_URL}/latest/opportunities"
params = {"limit": 1, "onlyData": "true"}

try:
    r = requests.get(url, auth=HTTPBasicAuth(ORACLE_USER, ORACLE_PASS), params=params, timeout=30)
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Response keys: {list(data.keys())}")
    print(f"Items count: {len(data.get('items', []))}")
    print(f"Has more: {data.get('hasMore', 'N/A')}")
    print(f"Total count: {data.get('count', 'N/A')}")
    
    if data.get('items'):
        print("\n✅ SUCCESS! Found opportunities.")
        print(json.dumps(data['items'][0], indent=2)[:500])
    else:
        print("\n⚠️  API returned 200 but ZERO items.")
        print("Full response:")
        print(json.dumps(data, indent=2))
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Try with finder (query parameter)
print("\n\nTest 2: Using Finder Query")
url = f"{BASE_URL}/latest/opportunities"
params = {
    "finder": "PrimaryKey",
    "limit": 10,
    "onlyData": "true"
}

try:
    r = requests.get(url, auth=HTTPBasicAuth(ORACLE_USER, ORACLE_PASS), params=params, timeout=30)
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Items: {len(data.get('items', []))}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Try without onlyData
print("\n\nTest 3: Without onlyData flag")
url = f"{BASE_URL}/latest/opportunities"
params = {"limit": 5}

try:
    r = requests.get(url, auth=HTTPBasicAuth(ORACLE_USER, ORACLE_PASS), params=params, timeout=30)
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Items: {len(data.get('items', []))}")
    if data.get('items'):
        print("✅ Found data without onlyData!")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Check user permissions endpoint
print("\n\nTest 4: Check Current User")
url = f"{BASE_URL}/latest/currentUser"

try:
    r = requests.get(url, auth=HTTPBasicAuth(ORACLE_USER, ORACLE_PASS), timeout=30)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        user_data = r.json()
        print(f"User: {user_data.get('UserName', 'N/A')}")
        print(f"Display Name: {user_data.get('DisplayName', 'N/A')}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n\n📊 DIAGNOSIS:")
print("If all tests show 0 items, the issue is:")
print("1. User doesn't have REST API access to opportunities")
print("2. Opportunities are filtered by security/territory")
print("3. Need to use a different API endpoint or service account")
print("\n💡 SOLUTION: Use the Selenium UI scraper instead (scripts/scrape_oracle_ui.py)")
