"""
Quick test script to verify the opportunities endpoint is working
"""
import requests

try:
    print("Testing /api/opportunities endpoint...")
    response = requests.get("http://127.0.0.1:8000/api/opportunities")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Found {len(data)} opportunities")
        
        if len(data) > 0:
            print("\nFirst opportunity:")
            print(f"  ID: {data[0].get('id')}")
            print(f"  Name: {data[0].get('name')}")
            print(f"  Status: {data[0].get('workflow_status')}")
            print(f"  Assigned SA: {data[0].get('assigned_sa')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to backend. Is it running on http://127.0.0.1:8000?")
except Exception as e:
    print(f"❌ Error: {e}")
