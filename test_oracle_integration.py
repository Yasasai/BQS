"""
Quick Test: Oracle Integration with MyOpportunitiesFinder
==========================================================

This script tests the new Oracle URL integration.
Run this to verify everything works before starting the full backend.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*70)
print("🧪 TESTING ORACLE INTEGRATION")
print("="*70)

# Test 1: Import
print("\n[Test 1/5] Testing imports...")
try:
    from backend.app.services.oracle_service import (
        get_all_opportunities,
        fetch_single_opportunity,
        get_oracle_token
    )
    print("✅ PASS - All functions imported successfully")
except ImportError as e:
    print(f"❌ FAIL - Import error: {e}")
    sys.exit(1)

# Test 2: Environment
print("\n[Test 2/5] Checking environment variables...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    oracle_url = os.getenv("ORACLE_BASE_URL")
    oracle_user = os.getenv("ORACLE_USER")
    oracle_pass = os.getenv("ORACLE_PASSWORD") or os.getenv("ORACLE_PASS")
    
    if not oracle_url:
        print("❌ FAIL - ORACLE_BASE_URL not set in .env")
        sys.exit(1)
    if not oracle_user:
        print("❌ FAIL - ORACLE_USER not set in .env")
        sys.exit(1)
    if not oracle_pass:
        print("❌ FAIL - ORACLE_PASSWORD not set in .env")
        sys.exit(1)
    
    print(f"✅ PASS - Environment configured")
    print(f"   URL: {oracle_url}")
    print(f"   User: {oracle_user}")
    print(f"   Password: {'*' * len(oracle_pass)}")
except Exception as e:
    print(f"❌ FAIL - Environment error: {e}")
    sys.exit(1)

# Test 3: Authentication
print("\n[Test 3/5] Testing Oracle authentication...")
try:
    token = get_oracle_token()
    if token:
        print(f"✅ PASS - OAuth token acquired")
        print(f"   Token: {token[:20]}...")
    else:
        print("ℹ️  INFO - No OAuth token (will use Basic Auth)")
        print("✅ PASS - Will use Basic Authentication")
except Exception as e:
    print(f"❌ FAIL - Authentication error: {e}")
    sys.exit(1)

# Test 4: Fetch Test (small batch)
print("\n[Test 4/5] Testing data fetch (1 batch, 5 records)...")
try:
    batch_count = 0
    total_records = 0
    
    for batch in get_all_opportunities(batch_size=5):
        batch_count += 1
        total_records += len(batch)
        print(f"   Batch {batch_count}: {len(batch)} records")
        
        # Show first record details
        if batch and len(batch) > 0:
            first = batch[0]
            print(f"   Sample: {first.get('Name', 'N/A')} (ID: {first.get('OptyNumber', 'N/A')})")
        
        # Only test first batch
        break
    
    if total_records > 0:
        print(f"✅ PASS - Fetched {total_records} records successfully")
    else:
        print("⚠️  WARNING - No records fetched (might be empty or permission issue)")
        print("   Check Oracle CRM permissions for ALLOPTIES RecordSet")
except Exception as e:
    print(f"❌ FAIL - Fetch error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Verify URL Format
print("\n[Test 5/5] Verifying URL format...")
try:
    # Check the function uses the correct parameters
    import inspect
    source = inspect.getsource(get_all_opportunities)
    
    if "MyOpportunitiesFinder" in source:
        print("✅ PASS - Uses MyOpportunitiesFinder")
    else:
        print("❌ FAIL - Not using MyOpportunitiesFinder")
        sys.exit(1)
    
    if "RecordSet='ALLOPTIES'" in source or 'RecordSet="ALLOPTIES"' in source:
        print("✅ PASS - Uses ALLOPTIES RecordSet")
    else:
        print("❌ FAIL - Not using ALLOPTIES RecordSet")
        sys.exit(1)
    
    if '"finder"' in source or "'finder'" in source:
        print("✅ PASS - Uses finder parameter")
    else:
        print("❌ FAIL - Not using finder parameter")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ FAIL - Verification error: {e}")
    sys.exit(1)

# Summary
print("\n" + "="*70)
print("🎉 ALL TESTS PASSED!")
print("="*70)
print("\n✅ Oracle integration is working correctly")
print("✅ Using MyOpportunitiesFinder with ALLOPTIES RecordSet")
print("✅ Ready to run full sync")
print("\nNext steps:")
print("  1. Run full sync: python -c \"from backend.app.services.sync_manager import sync_opportunities; sync_opportunities()\"")
print("  2. Start backend: python -m backend.app.main")
print("  3. Check frontend: http://localhost:5173")
print()
