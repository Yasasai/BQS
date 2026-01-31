
import requests
import json
import sys

try:
    print("Testing API: http://127.0.0.1:8000/api/opportunities/")
    r = requests.get('http://127.0.0.1:8000/api/opportunities/')
    
    if r.status_code != 200:
        print(f"❌ API Error: {r.status_code}")
        print(r.text)
        sys.exit(1)
        
    data = r.json()
    print(f"✅ API Success. Count: {len(data)}")
    
    if len(data) == 0:
        print("⚠️ Warning: API returned 0 opportunities.")
    
    unassigned_count = 0
    for o in data:
        # Check assigned_sa field specifically
        sa = o.get('assigned_sa')
        status = o.get('workflow_status')
        
        is_unassigned = (sa is None) or (sa == 'Unassigned')
        
        if is_unassigned:
            unassigned_count += 1
            print(f"   🔹 ID: {o.get('id')} | SA: {sa} (NULL/Unassigned) | Status: {status}")
        else:
            # print(f"   🔸 ID: {o.get('id')} | SA: {sa} | Status: {status}")
            pass

    print(f"\nTotal Unassigned found in JSON: {unassigned_count}")

except Exception as e:
    print(f"❌ Connection Failed: {e}")
