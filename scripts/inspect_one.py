import requests
import json
import os

# Config
BASE_URL = "https://eijs-test.fa.em2.oraclecloud.com"
USERNAME = "yasasvi.upadrasta@inspiraenterprise.com"
PASSWORD = "Welcome@123"
OPTY_ID = "1602737" # The ID user mentioned

def inspect_one():
    url = f"{BASE_URL}/crmRestApi/resources/latest/opportunities/{OPTY_ID}"
    print(f"Fetching {url}...")
    
    try:
        response = requests.get(url, auth=(USERNAME, PASSWORD))
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Successfully fetched Opportunity!")
            print(f"Name: {data.get('Name')}")
            print(f"OptyNumber: {data.get('OptyNumber')}")
            print(f"StatusCode: {data.get('StatusCode')}")
            print(f"SalesStage: {data.get('SalesStage')}")
            
            # Print all keys to help user see what's available
            # print("\nAll Fields:")
            # print(json.dumps(data, indent=2))
        else:
            print(f"❌ Failed: {response.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_one()
