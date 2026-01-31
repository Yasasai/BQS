import requests
import json

print("=" * 60)
print("Testing Backend API")
print("=" * 60)

try:
    # Test 1: Check if backend is running
    print("\n1️⃣ Testing backend connection...")
    response = requests.get("http://127.0.0.1:8000/api/opportunities", timeout=5)
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success! Received {len(data)} opportunities")
        
        if len(data) > 0:
            print("\n2️⃣ First opportunity details:")
            first = data[0]
            print(f"   ID: {first.get('id')}")
            print(f"   Name: {first.get('name')}")
            print(f"   Workflow Status: {first.get('workflow_status')}")
            print(f"   Assigned SA: {first.get('assigned_sa')}")
            
            print("\n3️⃣ All opportunities summary:")
            for i, opp in enumerate(data[:5], 1):
                print(f"   {i}. {opp.get('name')} - Status: {opp.get('workflow_status')} - SA: {opp.get('assigned_sa')}")
            
            if len(data) > 5:
                print(f"   ... and {len(data) - 5} more")
                
            # Count by status
            print("\n4️⃣ Count by workflow_status:")
            status_counts = {}
            for opp in data:
                status = opp.get('workflow_status') or 'NULL'
                status_counts[status] = status_counts.get(status, 0) + 1
            
            for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"   {status}: {count}")
                
        else:
            print("\n   ⚠️ Backend returned empty array!")
            print("   This means no opportunities in database or filtering issue.")
    else:
        print(f"   ❌ Error: HTTP {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
except requests.exceptions.ConnectionError:
    print("   ❌ Cannot connect to backend!")
    print("   Make sure backend is running: python -m uvicorn app.main:app --reload")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
