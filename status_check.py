
import requests
import time

def check_service(name, url):
    try:
        r = requests.get(url, timeout=2)
        print(f"✅ {name} is reachable ({r.status_code})")
        return True
    except Exception as e:
        print(f"❌ {name} unreachable: {e}")
        return False

# Backend
backend_ok = False
for i in range(5):
    if check_service("Backend", "http://127.0.0.1:8000/docs"):
        backend_ok = True
        break
    time.sleep(1)

# Frontend
frontend_ok = False
for i in range(5):
    if check_service("Frontend", "http://127.0.0.1:5176"):
        frontend_ok = True
        break
    time.sleep(1)
    
if backend_ok and frontend_ok:
    print("SUCCESS: Both services running.")
else:
    print("WARNING: One or both services failed.")
