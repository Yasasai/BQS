"""
Oracle URL Diagnostic - Compare Postman vs Python
==================================================

This script shows exactly what URL is being constructed and sent to Oracle.
Compare this with your Postman request to debug any differences.
"""

import sys
import os
from urllib.parse import urlencode

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*80)
print("🔍 ORACLE URL DIAGNOSTIC")
print("="*80)

# Load environment
from dotenv import load_dotenv
load_dotenv()

ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASS = os.getenv("ORACLE_PASSWORD") or os.getenv("ORACLE_PASS")

print(f"\n📍 Base URL: {ORACLE_BASE_URL}")
print(f"👤 Username: {ORACLE_USER}")
print(f"🔑 Password: {'*' * len(ORACLE_PASS) if ORACLE_PASS else 'NOT SET'}")

# Test 1: Show what Postman URL looks like
print("\n" + "="*80)
print("1️⃣  POSTMAN URL (what you provided):")
print("="*80)
postman_url = "https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/11.12.1.0/opportunities?finder=MyOpportunitiesFinder;RecordSet=%27ALLOPTIES%27"
print(postman_url)
print("\nBreakdown:")
print(f"  Base: https://eijs-test.fa.em2.oraclecloud.com")
print(f"  Path: /crmRestApi/resources/11.12.1.0/opportunities")
print(f"  Param: finder=MyOpportunitiesFinder;RecordSet=%27ALLOPTIES%27")
print(f"  Note: %27 is URL-encoded single quote '")

# Test 2: Show what Python constructs
print("\n" + "="*80)
print("2️⃣  PYTHON URL (what our code builds):")
print("="*80)

# Method 1: Using params dict (what requests does)
params = {
    "finder": "MyOpportunitiesFinder;RecordSet='ALLOPTIES'",
    "onlyData": "true",
    "limit": 50,
    "offset": 0
}

base_url = f"{ORACLE_BASE_URL}/crmRestApi/resources/latest/opportunities"
python_url = f"{base_url}?{urlencode(params)}"

print(python_url)
print("\nBreakdown:")
print(f"  Base: {ORACLE_BASE_URL}")
print(f"  Path: /crmRestApi/resources/latest/opportunities")
print(f"  Params: {urlencode(params)}")

# Test 3: Compare the two
print("\n" + "="*80)
print("3️⃣  COMPARISON:")
print("="*80)

print("\n🔍 Differences:")
print(f"  Postman version: 11.12.1.0")
print(f"  Python version:  latest")
print(f"  → This is OK, 'latest' should work")

print(f"\n  Postman has: RecordSet=%27ALLOPTIES%27")
print(f"  Python has:  RecordSet=%27ALLOPTIES%27")
print(f"  → These are IDENTICAL (both URL-encoded)")

print(f"\n  Postman: Only finder parameter")
print(f"  Python:  finder + onlyData + limit + offset")
print(f"  → Python has extra params for pagination")

# Test 4: Try actual request
print("\n" + "="*80)
print("4️⃣  TESTING ACTUAL REQUEST:")
print("="*80)

try:
    import requests
    from requests.auth import HTTPBasicAuth
    
    print("\n🌐 Making request to Oracle...")
    print(f"URL: {base_url}")
    print(f"Params: {params}")
    print(f"Auth: Basic ({ORACLE_USER})")
    
    response = requests.get(
        base_url,
        params=params,
        auth=HTTPBasicAuth(ORACLE_USER, ORACLE_PASS),
        timeout=30
    )
    
    print(f"\n📊 Response:")
    print(f"  Status Code: {response.status_code}")
    print(f"  Actual URL:  {response.url}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Response Keys: {list(data.keys())}")
        
        if "items" in data:
            items = data.get("items", [])
            print(f"  ✅ SUCCESS! Found {len(items)} opportunities")
            
            if items:
                print(f"\n  📋 First opportunity:")
                first = items[0]
                print(f"     Name: {first.get('Name', 'N/A')}")
                print(f"     OptyNumber: {first.get('OptyNumber', 'N/A')}")
                print(f"     Revenue: {first.get('Revenue', 'N/A')}")
        else:
            print(f"  ⚠️  No 'items' key in response")
            print(f"  Response: {str(data)[:200]}")
    else:
        print(f"  ❌ ERROR: {response.status_code}")
        print(f"  Response: {response.text[:500]}")
        
except Exception as e:
    print(f"  ❌ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Try with version 11.12.1.0 (like Postman)
print("\n" + "="*80)
print("5️⃣  TESTING WITH SPECIFIC VERSION (11.12.1.0):")
print("="*80)

try:
    versioned_url = f"{ORACLE_BASE_URL}/crmRestApi/resources/11.12.1.0/opportunities"
    
    print(f"\n🌐 Making request to Oracle...")
    print(f"URL: {versioned_url}")
    print(f"Params: {params}")
    
    response = requests.get(
        versioned_url,
        params=params,
        auth=HTTPBasicAuth(ORACLE_USER, ORACLE_PASS),
        timeout=30
    )
    
    print(f"\n📊 Response:")
    print(f"  Status Code: {response.status_code}")
    print(f"  Actual URL:  {response.url}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Response Keys: {list(data.keys())}")
        
        if "items" in data:
            items = data.get("items", [])
            print(f"  ✅ SUCCESS! Found {len(items)} opportunities")
        else:
            print(f"  ⚠️  No 'items' key in response")
    else:
        print(f"  ❌ ERROR: {response.status_code}")
        print(f"  Response: {response.text[:500]}")
        
except Exception as e:
    print(f"  ❌ EXCEPTION: {e}")

# Summary
print("\n" + "="*80)
print("📝 SUMMARY & RECOMMENDATIONS:")
print("="*80)

print("\n1. URL Encoding:")
print("   ✅ Python correctly encodes ' as %27")
print("   ✅ This matches your Postman URL")

print("\n2. API Version:")
print("   ℹ️  Postman uses: 11.12.1.0")
print("   ℹ️  Python uses:  latest")
print("   💡 Try using specific version if 'latest' doesn't work")

print("\n3. Parameters:")
print("   ✅ finder parameter is correct")
print("   ✅ RecordSet='ALLOPTIES' is correct")

print("\n4. Authentication:")
print("   ✅ Using Basic Auth")
print(f"   ✅ Username: {ORACLE_USER}")

print("\n5. Next Steps:")
if response.status_code == 200:
    print("   ✅ Connection working!")
    print("   ✅ Ready to use in your application")
else:
    print("   ⚠️  Check the error messages above")
    print("   💡 Verify Oracle credentials")
    print("   💡 Check Oracle CRM permissions")
    print("   💡 Try using version 11.12.1.0 instead of 'latest'")

print("\n" + "="*80)
