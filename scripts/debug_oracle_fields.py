import requests
import json
import os

# Config
BASE_URL = "https://eijs-test.fa.em2.oraclecloud.com"
USERNAME = "yasasvi.upadrasta@inspiraenterprise.com"
PASSWORD = "Welcome@123"

def check_fields():
    print("Testing Oracle Fields...")
    
    # 1. Fetch one record WITHOUT fields param to see what exists
    url = f"{BASE_URL}/crmRestApi/resources/latest/opportunities"
    params = {'limit': 1}
    
    try:
        print("\n--- Test 1: Fetch Default Fields ---")
        response = requests.get(url, auth=(USERNAME, PASSWORD), params=params)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            if items:
                print("✅ Success! Available keys in first item:")
                keys = sorted(list(items[0].keys()))
                print(", ".join(keys))
            else:
                print("⚠️ No items returned.")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")

    # 2. Test the specific detailed fields we want
    print("\n--- Test 2: Invalid Field Detection ---")
    candidate_fields = [
        'OptyId', 'OptyNumber', 'Name', 'Revenue', 'WinProb', 'SalesStage', 
        'OwnerName', 'PrimaryContactName', 'CloseDate', 'TargetPartyName', 
        'CurrencyCode', 'EffectiveDate', 'BusinessUnit', 'Territory', 'Industry', 'StatusCode'
    ]
    
    for field in candidate_fields:
        params = {'limit': 1, 'fields': field}
        try:
            resp = requests.get(url, auth=(USERNAME, PASSWORD), params=params)
            if resp.status_code == 200:
                print(f"✅ {field}: OK")
            else:
                print(f"❌ {field}: INVALID (Status {resp.status_code})")
        except:
            print(f"❌ {field}: Error")

if __name__ == "__main__":
    check_fields()
