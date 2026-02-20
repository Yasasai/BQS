
import sys
import os

sys.path.append(os.getcwd())

print("Testing imports...")
try:
    from backend.app.core.database import init_db
    print("✅ backend.app.core.database imported")
    
    from backend.app.routers import auth, inbox, scoring
    print("✅ backend.app.routers imported")
    
    import backend.main
    print("✅ backend.main imported")
    
    import backend.sync_manager
    print("✅ backend.sync_manager imported")
    
    print("All imports successful.")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
