import os
import sys
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from oracle_service import get_from_oracle

def probe_fields():
    print("🔍 Probing Oracle CRM for ALL available fields...")
    # Fetch just one record without field restrictions to see everything
    params = {"limit": 1, "onlyData": "true"}
    data = get_from_oracle("opportunities", params=params)
    
    if "items" in data and data["items"]:
        item = data["items"][0]
        print(f"\n✅ Found Opportunity: {item.get('OptyNumber')}")
        print("\n--- ALL AVAILABLE FIELDS ---")
        keys = sorted(item.keys())
        for key in keys:
            val = item[key]
            # Print key and a snippet of the value
            print(f"{key}: {str(val)[:50]}...")
            
        # Save to a file for analysis
        with open('oracle_field_probe.json', 'w') as f:
            json.dump(item, f, indent=4)
        print(f"\n📁 Full JSON saved to oracle_field_probe.json")
    else:
        print("❌ No items found or error occurred.")
        print(data)

if __name__ == "__main__":
    probe_fields()
