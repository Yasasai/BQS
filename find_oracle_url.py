"""
Dynamic Oracle API URL Finder
Automatically discovers the correct API endpoint version
"""
import requests
from requests.auth import HTTPBasicAuth
import re

ORACLE_USER = "yasasvi.upadrasta@inspiraenterprise.com"
ORACLE_PASS = "Welcome@123"
BASE_DOMAIN = "https://eijs-test.fa.em2.oraclecloud.com"

def find_working_api_url():
    """
    Dynamically find the working Oracle CRM REST API URL
    Returns: (base_url, version) or (None, None) if not found
    """
    print("🔍 Discovering Oracle API endpoint...\n")
    
    # List of possible API versions to try
    versions_to_try = [
        "latest",
        "11.13.18.05",
        "24.05",
        "23.11",
        "23.08",
        "22.11",
        "21.11",
        "20.11",
        "19.11",
    ]
    
    for version in versions_to_try:
        url = f"{BASE_DOMAIN}/crmRestApi/resources/{version}/opportunities"
        params = {"limit": 1, "onlyData": "true"}
        
        try:
            print(f"Testing: {version}...", end=" ")
            r = requests.get(
                url, 
                auth=HTTPBasicAuth(ORACLE_USER, ORACLE_PASS), 
                params=params, 
                timeout=10
            )
            
            if r.status_code == 200:
                print(f"✅ WORKS!")
                data = r.json()
                item_count = len(data.get("items", []))
                print(f"   Items returned: {item_count}")
                
                base_url = f"{BASE_DOMAIN}/crmRestApi/resources/{version}"
                return base_url, version
                
            elif r.status_code == 404:
                print(f"❌ 404 Not Found")
            elif r.status_code == 401:
                print(f"❌ 401 Unauthorized")
            else:
                print(f"⚠️  {r.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏱️  Timeout")
        except Exception as e:
            print(f"❌ Error: {str(e)[:50]}")
    
    print("\n❌ No working API endpoint found!")
    return None, None

def discover_api_metadata(base_url):
    """
    Get metadata about the API to understand available resources
    """
    print(f"\n📊 Fetching API metadata...")
    
    # Try to get the service document
    metadata_url = base_url.replace("/resources/", "/")
    
    try:
        r = requests.get(
            metadata_url,
            auth=HTTPBasicAuth(ORACLE_USER, ORACLE_PASS),
            timeout=10
        )
        
        if r.status_code == 200:
            print(f"✅ Metadata available at: {metadata_url}")
            # Look for version info in response
            content = r.text
            version_match = re.search(r'version["\s:]+([0-9.]+)', content, re.IGNORECASE)
            if version_match:
                print(f"   API Version: {version_match.group(1)}")
        else:
            print(f"⚠️  Metadata not accessible ({r.status_code})")
            
    except Exception as e:
        print(f"⚠️  Could not fetch metadata: {e}")

def test_opportunity_access(base_url):
    """
    Test different ways to access opportunities
    """
    print(f"\n🧪 Testing opportunity access methods...\n")
    
    test_cases = [
        ("Default (no params)", {}),
        ("With onlyData", {"onlyData": "true"}),
        ("With limit", {"limit": 10}),
        ("With fields", {"fields": "OptyId,Name,Revenue"}),
        ("With orderBy", {"orderBy": "LastUpdateDate:desc", "limit": 5}),
    ]
    
    url = f"{base_url}/opportunities"
    
    for test_name, params in test_cases:
        try:
            print(f"{test_name}...", end=" ")
            r = requests.get(
                url,
                auth=HTTPBasicAuth(ORACLE_USER, ORACLE_PASS),
                params=params,
                timeout=10
            )
            
            if r.status_code == 200:
                data = r.json()
                count = len(data.get("items", []))
                print(f"✅ {count} items")
            else:
                print(f"❌ {r.status_code}")
                
        except Exception as e:
            print(f"❌ {str(e)[:30]}")

def save_config(base_url, version):
    """
    Save the working URL to a config file
    """
    config_content = f"""# Oracle API Configuration (Auto-discovered)
ORACLE_BASE_URL={base_url}
ORACLE_API_VERSION={version}
ORACLE_OPPORTUNITIES_ENDPOINT={base_url}/opportunities

# Full URL for opportunities:
# {base_url}/opportunities

# Generated: {__import__('datetime').datetime.now()}
"""
    
    with open("oracle_api_config.txt", "w") as f:
        f.write(config_content)
    
    print(f"\n💾 Configuration saved to: oracle_api_config.txt")

if __name__ == "__main__":
    print("=" * 70)
    print("Oracle API Dynamic URL Finder")
    print("=" * 70)
    
    # Step 1: Find working URL
    base_url, version = find_working_api_url()
    
    if base_url:
        print(f"\n🎉 SUCCESS!")
        print(f"Working Base URL: {base_url}")
        print(f"API Version: {version}")
        
        # Step 2: Get metadata
        discover_api_metadata(base_url)
        
        # Step 3: Test access methods
        test_opportunity_access(base_url)
        
        # Step 4: Save config
        save_config(base_url, version)
        
        print("\n" + "=" * 70)
        print("✅ Use this URL in your scripts:")
        print(f"   {base_url}/opportunities")
        print("=" * 70)
    else:
        print("\n💡 RECOMMENDATIONS:")
        print("1. Check if your credentials are correct")
        print("2. Verify you have REST API access in Oracle")
        print("3. Contact your Oracle admin for the correct API version")
        print("4. Use the Selenium UI scraper as an alternative")
