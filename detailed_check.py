import requests
import time

print("Attempting to connect to backend...")
try:
    response = requests.get("http://localhost:8000/api/opportunities", timeout=5)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Found {len(data)} opportunities.")
    else:
        print("Backend reachable but returned error.")
except Exception as e:
    print(f"Could not connect: {e}")
