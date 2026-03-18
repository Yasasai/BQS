
import os
import sys

# Add project root to path
sys.path.append(r"c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS")

from batch_sync_with_offset import get_sync_status, get_synced_count

try:
    status = get_sync_status("oracle_opportunities")
    count = get_synced_count()
    print(f"Status: {status}")
    print(f"Count: {count}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
