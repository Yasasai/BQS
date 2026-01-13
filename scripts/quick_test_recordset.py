
import os
import sys
# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from oracle_service import get_from_oracle
import json

def test_recordset():
    # Attempt to fetch exactly 1602737 with RecordSet=ALL
    endpoint = "opportunities"
    params = {
        "q": "RecordSet='ALL';OptyNumber='1602737'",
        "onlyData": "true",
        "limit": 1
    }
    
    print(f"Testing fetch for Opty 1602737 with RecordSet='ALL'...")
    data = get_from_oracle(endpoint, params=params)
    
    if "error" in data:
        print(f"FAILED: {data['error']}")
    else:
        items = data.get("items", [])
        if items:
            print("SUCCESS! Record found.")
            print(json.dumps(items[0], indent=2))
        else:
            print("FAILED: Record still not found even with RecordSet='ALL'.")

if __name__ == "__main__":
    test_recordset()
