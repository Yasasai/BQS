"""
Simple backend health check
"""
import requests

print("Checking backend health...")
print()

try:
    # Simple ping
    response = requests.get("http://localhost:8000/", timeout=30)
    print("✓ Backend is responding!")
    print(f"Response: {response.json()}")
    print()
    
    # Check if sync endpoint exists
    print("Checking sync endpoint...")
    response = requests.post("http://localhost:8000/api/sync-database", timeout=30)
    print(f"✓ Sync endpoint responded with status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    print("✅ Backend is healthy and sync has been triggered!")
    print()
    print("Check your backend console for sync progress.")
    
except requests.exceptions.Timeout:
    print("⚠️  Backend is slow to respond (timeout after 30 seconds)")
    print()
    print("This might mean:")
    print("  - Backend is processing a heavy request")
    print("  - Oracle CRM connection is slow")
    print("  - Database is busy")
    print()
    print("Check your backend console to see what it's doing.")
    
except requests.exceptions.ConnectionError:
    print("✗ Backend is NOT running!")
    print()
    print("Make sure you have started the backend:")
    print("  python backend/main.py")
    
except Exception as e:
    print(f"✗ Error: {e}")
    print()
    print("Check backend console for errors.")

print()
input("Press Enter to exit...")
