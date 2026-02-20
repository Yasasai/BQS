
import sys
import os
import asyncio

# Setup path: backend/run_sync_and_log.py -> backend -> BQS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Redirect stdout/stderr
log_file = os.path.join(BASE_DIR, "full_sync.log")
sys.stdout = open(log_file, "w", encoding="utf-8")
sys.stderr = sys.stdout

print("Starting Sync via Wrapper...")

try:
    # Ensure backend is in path
    if BASE_DIR not in sys.path:
        sys.path.append(BASE_DIR)
        
    from backend.app.services.async_sync import run_async_sync
    asyncio.run(run_async_sync())
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
