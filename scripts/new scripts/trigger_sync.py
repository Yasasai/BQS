"""
Trigger immediate Oracle CRM sync
Run this while backend is running to perform an immediate sync
"""
import requests
import sys
import time

print("="*60)
print("🔄 Triggering Immediate Oracle CRM Sync")
print("="*60)
print()

backend_url = "http://localhost:8000"

# Check if backend is running with longer timeout
try:
    print("Checking backend status...")
    response = requests.get(f"{backend_url}/", timeout=30)
    print(f"✓ Backend is running: {response.json()}")
    print()
except requests.exceptions.Timeout:
    print("⚠️  Backend is slow to respond but might be running...")
    print("Attempting to trigger sync anyway...")
    print()
except requests.exceptions.ConnectionError:
    print("✗ ERROR: Backend is not running!")
    print("Please ensure backend is running: python backend/main.py")
    print()
    input("Press Enter to exit...")
    sys.exit(1)
except Exception as e:
    print(f"⚠️  Warning: {e}")
    print("Attempting to trigger sync anyway...")
    print()

# Trigger sync with longer timeout
try:
    print("Triggering sync (this may take a moment)...")
    response = requests.post(f"{backend_url}/api/sync-database", timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ {result.get('message', 'Sync triggered successfully!')}")
        print()
        print("="*60)
        print("📊 Sync is Running in Background")
        print("="*60)
        print()
        print("The sync process has been started.")
        print("Watch your backend console for detailed progress.")
        print()
        print("You should see output like:")
        print("  🔄 FULL SYNC - First time synchronization")
        print("  📡 Fetching opportunities from Oracle CRM...")
        print("  ✓ Fetched X opportunities from Oracle")
        print("  💾 Syncing to PostgreSQL...")
        print()
        
        # Wait a bit for sync to start
        print("Waiting for sync to start...")
        time.sleep(5)
        
        # Try to get status
        try:
            status_response = requests.get(f"{backend_url}/api/sync-status", timeout=10)
            if status_response.status_code == 200:
                status = status_response.json()
                if status.get('sync_type'):
                    print()
                    print("Latest Sync Status:")
                    print(f"  Type: {status.get('sync_type', 'N/A')}")
                    print(f"  Status: {status.get('status', 'N/A')}")
                    print(f"  Records Fetched: {status.get('total_fetched', 0)}")
                    print(f"  New Records: {status.get('new_records', 0)}")
                    print(f"  Updated Records: {status.get('updated_records', 0)}")
                else:
                    print()
                    print("Sync is still initializing...")
        except:
            print()
            print("Sync status will be available shortly.")
        
        print()
        print("="*60)
        print("✅ Sync initiated successfully!")
        print("="*60)
        print()
        print("To check status later:")
        print(f"  Visit: {backend_url}/api/sync-status")
        print(f"  Or: {backend_url}/docs")
        print()
        
    else:
        print(f"✗ ERROR: Sync failed with status {response.status_code}")
        print(f"Response: {response.text}")
        print()
        input("Press Enter to exit...")
        sys.exit(1)
        
except requests.exceptions.Timeout:
    print()
    print("⚠️  Request timed out, but sync may still be running!")
    print()
    print("This can happen if:")
    print("  1. Oracle CRM is slow to respond")
    print("  2. There are many opportunities to sync")
    print("  3. Network connection is slow")
    print()
    print("Check your backend console for sync progress.")
    print(f"Or visit: {backend_url}/api/sync-status")
    print()
    
except requests.exceptions.ConnectionError:
    print()
    print("✗ ERROR: Cannot connect to backend!")
    print()
    print("Please ensure:")
    print("  1. Backend is running (python backend/main.py)")
    print("  2. Backend is on port 8000")
    print("  3. No firewall blocking localhost:8000")
    print()
    input("Press Enter to exit...")
    sys.exit(1)
    
except Exception as e:
    print()
    print(f"✗ ERROR: {e}")
    print()
    print("Check backend console for errors.")
    print()
    input("Press Enter to exit...")
    sys.exit(1)

print()
input("Press Enter to exit...")
