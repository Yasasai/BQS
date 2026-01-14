"""
Oracle Opportunity ID Fetcher - All Methods
Tries every possible way to get opportunity IDs from Oracle CRM
"""
import requests
from requests.auth import HTTPBasicAuth
import json

ORACLE_USER = "yasasvi.upadrasta@inspiraenterprise.com"
ORACLE_PASS = "Welcome@123"
BASE_URL = "https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/11.13.18.05"

def method_1_standard_get():
    """Method 1: Standard GET /opportunities"""
    print("\n" + "="*70)
    print("METHOD 1: Standard GET Request")
    print("="*70)
    
    url = f"{BASE_URL}/opportunities"
    params = {
        "onlyData": "true",
        "limit": 100,
        "fields": "OptyId,OptyNumber,Name,Revenue,WinProb"
    }
    
    try:
        r = requests.get(url, auth=HTTPBasicAuth(ORACLE_USER, ORACLE_PASS), params=params, timeout=30)
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            items = data.get("items", [])
            print(f"Items found: {len(items)}")
            
            if items:
                print("\n✅ SUCCESS! Sample:")
                print(json.dumps(items[0], indent=2)[:500])
                return items
            else:
                print("⚠️  Response OK but 0 items")
                print(f"Response keys: {list(data.keys())}")
        else:
            print(f"❌ Failed: {r.text[:200]}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return []

def method_2_finder_query():
    """Method 2: Use Finder with specific criteria"""
    print("\n" + "="*70)
    print("METHOD 2: Finder Query (All Open Opportunities)")
    print("="*70)
    
    url = f"{BASE_URL}/opportunities"
    
    # Try different finder queries
    finders = [
        ("MyOpportunities", {"finder": "MyOpportunities"}),
        ("OpenOpportunities", {"finder": "OpenOpportunities"}),
        ("AllOpportunities", {"finder": "AllOpportunities"}),
        ("PrimaryKey", {"finder": "PrimaryKey", "limit": 10}),
    ]
    
    for finder_name, params in finders:
        try:
            print(f"\nTrying finder: {finder_name}...", end=" ")
            params["onlyData"] = "true"
            
            r = requests.get(url, auth=HTTPBasicAuth(ORACLE_USER, ORACLE_PASS), params=params, timeout=30)
            
            if r.status_code == 200:
                data = r.json()
                items = data.get("items", [])
                print(f"✅ {len(items)} items")
                
                if items:
                    print(f"   Sample ID: {items[0].get('OptyId')} - {items[0].get('Name')}")
                    return items
            else:
                print(f"❌ {r.status_code}")
                
        except Exception as e:
            print(f"❌ {str(e)[:50]}")
    
    return []

def method_3_describe_endpoint():
    """Method 3: Get metadata to understand available finders"""
    print("\n" + "="*70)
    print("METHOD 3: Describe Endpoint (Get Available Finders)")
    print("="*70)
    
    url = f"{BASE_URL}/opportunities/describe"
    
    try:
        r = requests.get(url, auth=HTTPBasicAuth(ORACLE_USER, ORACLE_PASS), timeout=30)
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            
            # Look for finders
            if "finders" in data:
                print("\n✅ Available Finders:")
                for finder in data["finders"]:
                    print(f"   - {finder.get('name')}: {finder.get('description', 'N/A')}")
            
            # Look for child resources
            if "links" in data:
                print("\n📎 Available Links/Resources:")
                for link in data["links"][:5]:
                    print(f"   - {link.get('rel')}: {link.get('href', 'N/A')}")
                    
            return data
        else:
            print(f"❌ {r.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def method_4_batch_request():
    """Method 4: Batch request for multiple IDs"""
    print("\n" + "="*70)
    print("METHOD 4: Batch Request")
    print("="*70)
    
    # If you have some OptyNumbers from the UI, try batch fetch
    known_numbers = ["1602737", "1553327", "16985449"]  # From your screenshot
    
    url = f"{BASE_URL}/opportunities"
    
    for opty_num in known_numbers:
        try:
            print(f"\nFetching OptyNumber={opty_num}...", end=" ")
            params = {
                "q": f"OptyNumber={opty_num}",
                "onlyData": "true"
            }
            
            r = requests.get(url, auth=HTTPBasicAuth(ORACLE_USER, ORACLE_PASS), params=params, timeout=30)
            
            if r.status_code == 200:
                data = r.json()
                items = data.get("items", [])
                
                if items:
                    opty = items[0]
                    print(f"✅ Found!")
                    print(f"   OptyId: {opty.get('OptyId')}")
                    print(f"   Name: {opty.get('Name')}")
                    print(f"   Revenue: {opty.get('Revenue')}")
                else:
                    print(f"⚠️  Not found")
            else:
                print(f"❌ {r.status_code}")
                
        except Exception as e:
            print(f"❌ {str(e)[:50]}")

def method_5_child_resources():
    """Method 5: Try accessing child resources that might have IDs"""
    print("\n" + "="*70)
    print("METHOD 5: Child Resources (Revenue, Contacts, etc.)")
    print("="*70)
    
    # Try accessing related resources that might expose opportunity IDs
    child_endpoints = [
        "OpportunityRevenue",
        "OpportunityContact", 
        "OpportunityCompetitor",
        "OpportunityResource",
    ]
    
    for endpoint in child_endpoints:
        try:
            url = f"{BASE_URL}/{endpoint}"
            print(f"\nTrying {endpoint}...", end=" ")
            
            r = requests.get(
                url, 
                auth=HTTPBasicAuth(ORACLE_USER, ORACLE_PASS),
                params={"limit": 5, "onlyData": "true"},
                timeout=30
            )
            
            if r.status_code == 200:
                data = r.json()
                items = data.get("items", [])
                print(f"✅ {len(items)} items")
                
                if items:
                    # These child resources should have OptyId references
                    print(f"   Sample: {json.dumps(items[0], indent=2)[:300]}")
            else:
                print(f"❌ {r.status_code}")
                
        except Exception as e:
            print(f"❌ {str(e)[:30]}")

def method_6_raw_sql_query():
    """Method 6: Try using SQL-like query"""
    print("\n" + "="*70)
    print("METHOD 6: SQL-Style Query")
    print("="*70)
    
    url = f"{BASE_URL}/opportunities"
    
    queries = [
        "StatusCode='OPEN'",
        "Revenue > 0",
        "CreationDate > '2020-01-01'",
        "OptyId IS NOT NULL",
    ]
    
    for query in queries:
        try:
            print(f"\nQuery: {query}...", end=" ")
            params = {
                "q": query,
                "onlyData": "true",
                "limit": 10
            }
            
            r = requests.get(url, auth=HTTPBasicAuth(ORACLE_USER, ORACLE_PASS), params=params, timeout=30)
            
            if r.status_code == 200:
                data = r.json()
                items = data.get("items", [])
                print(f"✅ {len(items)} items")
                
                if items:
                    return items
            else:
                print(f"❌ {r.status_code}")
                
        except Exception as e:
            print(f"❌ {str(e)[:30]}")
    
    return []

if __name__ == "__main__":
    print("="*70)
    print("ORACLE OPPORTUNITY ID FETCHER - ALL METHODS")
    print("="*70)
    print("Testing every possible way to get opportunity data with IDs...")
    
    results = []
    
    # Try all methods
    results.extend(method_1_standard_get())
    
    if not results:
        results.extend(method_2_finder_query())
    
    if not results:
        method_3_describe_endpoint()
    
    if not results:
        method_4_batch_request()
    
    if not results:
        method_5_child_resources()
    
    if not results:
        results.extend(method_6_raw_sql_query())
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    if results:
        print(f"✅ SUCCESS! Found {len(results)} opportunities")
        print("\nSample IDs:")
        for opty in results[:5]:
            print(f"   {opty.get('OptyId')} - {opty.get('Name')}")
        
        # Save to file
        with open("fetched_opportunities.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Saved to: fetched_opportunities.json")
    else:
        print("❌ No opportunities found with any method")
        print("\n💡 NEXT STEPS:")
        print("1. Use the Selenium UI scraper (scripts/scrape_oracle_ui.py)")
        print("2. Contact Oracle admin to enable REST API access")
        print("3. Check if your user has 'Sales Representative' or 'Sales Manager' role")
