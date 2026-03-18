import sys
import traceback
import os
sys.path.append(os.path.dirname(__file__))

with open("test_out.txt", "w") as f:
    sys.stdout = f
    sys.stderr = f
    try:
        from backend.app.services.sync_manager import sync_opportunities
        sync_opportunities()
    except Exception as e:
        traceback.print_exc()
