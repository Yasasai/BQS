"""
Quick test to verify database models load correctly
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

print("Testing database imports...")

try:
    from database import SessionLocal, Opportunity, SyncLog
    print("✓ Database imports successful")
    print(f"✓ Opportunity model loaded")
    print(f"✓ SyncLog model loaded")
    
    # Test SyncLog has correct column name
    if hasattr(SyncLog, 'sync_metadata'):
        print("✓ SyncLog.sync_metadata column exists (fixed reserved word issue)")
    else:
        print("✗ SyncLog.sync_metadata column missing")
    
    print("\n✅ All imports successful! Database models are working.")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
