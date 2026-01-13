import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from oracle_service import fetch_single_opportunity, get_from_oracle

def test_fetch():
    opty_number = "1602737"
    print(f"Fetching details for OptyNumber: {opty_number}")
    
    result = fetch_single_opportunity(opty_number)
    
    if result:
        print("Successfully fetched opportunity details!")
        # Print keys to understand structure
        print(f"Available fields: {list(result.keys())}")
        # Save to file for offline analysis if needed
        with open('oracle_sample_response.json', 'wb') as f:
            f.write(json.dumps(result, indent=2).encode('utf-8'))
        print("Sample response saved to oracle_sample_response.json")
        
        # Check specific fields user mentioned
        print(f"Name: {result.get('Name')}")
        print(f"OptyNumber: {result.get('OptyNumber')}")
        print(f"OptyId: {result.get('OptyId')}")
    else:
        print("Failed to fetch opportunity. Check credentials and connection.")

if __name__ == "__main__":
    test_fetch()
