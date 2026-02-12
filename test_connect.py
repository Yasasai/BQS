
import requests
import sys

try:
    print("Checking backend...")
    r = requests.get("http://127.0.0.1:8000/docs", timeout=5)
    print(f"Backend status: {r.status_code}")
except Exception as e:
    print(f"Backend error: {e}")
