import requests
import os
import json

# Configuration
ORACLE_BASE_URL = "https://eijs-test.fa.em2.oraclecloud.com"
ORACLE_USERNAME = "yasasvi.upadrasta@inspiraenterprise.com"
ORACLE_PASSWORD = "Welcome@123"
ENDPOINT = "/crmRestApi/resources/latest/opportunities"

def discover_fields():
    print("Fetching one opportunity to discover fields...")
    
    url = f"{ORACLE_BASE_URL}{ENDPOINT}"
    params = {
        'limit': 1,
        'q': 'StatusCode=OPEN'
    }
    
    try:
        response = requests.get(
            url, 
            auth=(ORACLE_USERNAME, ORACLE_PASSWORD),
            params=params, 
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        items = data.get('items', [])
        
        if items:
            print("\n✅ Successfully fetched an opportunity!")
            item = items[0]
            print("\nAvailable Fields:")
            for key, value in item.items():
                print(f"{key}: {value}")
                
            # Save to file for easy reading
            with open('oracle_fields_dump.json', 'w') as f:
                json.dump(item, f, indent=2)
            print("\nSaved full field list to 'oracle_fields_dump.json'")
        else:
            print("No opportunities found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    discover_fields()
