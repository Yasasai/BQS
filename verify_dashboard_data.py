"""
Verify Dashboard Data Setup
This script checks if opportunities are properly configured to display on the dashboard
"""
import requests
from backend.app.core.database import get_db
from backend.app.models import Opportunity

print("\n" + "="*70)
print("DASHBOARD DATA VERIFICATION")
print("="*70 + "\n")

# Step 1: Check Database
print("📊 Step 1: Checking Database...")
try:
    db = next(get_db())
    opps = db.query(Opportunity).all()
    print(f"✅ Database Connection: SUCCESS")
    print(f"✅ Total Opportunities in DB: {len(opps)}")
    
    if len(opps) > 0:
        print(f"\n📋 Sample Opportunities:")
        for i, opp in enumerate(opps[:5], 1):
            print(f"   {i}. {opp.opp_name}")
            print(f"      Customer: {opp.customer_name}")
            print(f"      Value: ${opp.deal_value or 0:,.2f}")
            print(f"      Status: {opp.workflow_status or 'NEW'}")
            print()
    else:
        print("\n⚠️  WARNING: No opportunities found in database!")
        print("   You need to run the Oracle sync to populate data.")
        print("   Run: python batch_sync_with_offset.py")
        
except Exception as e:
    print(f"❌ Database Error: {e}")

# Step 2: Check Backend API
print("\n" + "-"*70)
print("🌐 Step 2: Checking Backend API...")
try:
    response = requests.get('http://localhost:8000/api/opportunities', timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API Endpoint: ACCESSIBLE")
        print(f"✅ API Response: {len(data)} opportunities")
        
        if len(data) > 0:
            print(f"\n📋 Sample API Response:")
            sample = data[0]
            print(f"   Name: {sample.get('name')}")
            print(f"   Customer: {sample.get('customer')}")
            print(f"   Value: ${sample.get('deal_value', 0):,.2f}")
            print(f"   Status: {sample.get('workflow_status')}")
    else:
        print(f"❌ API returned status code: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("❌ Backend API: NOT RUNNING")
    print("   Start the backend with: cd backend && uvicorn app.main:app --reload")
except Exception as e:
    print(f"❌ API Error: {e}")

# Step 3: Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

try:
    db_count = len(opps) if 'opps' in locals() else 0
    api_running = 'response' in locals() and response.status_code == 200
    
    if db_count > 0 and api_running:
        print("✅ READY: Dashboard should display opportunities!")
        print(f"   - Database has {db_count} opportunities")
        print(f"   - API is serving data correctly")
        print("\n🎯 Next Steps:")
        print("   1. Start frontend: cd frontend && npm run dev")
        print("   2. Open browser: http://localhost:5173")
        print("   3. Navigate to Management Dashboard or Practice Head Dashboard")
    elif db_count == 0:
        print("⚠️  ACTION REQUIRED: No data in database")
        print("\n🎯 Next Steps:")
        print("   1. Run Oracle sync: python batch_sync_with_offset.py")
        print("   2. Restart backend if needed")
        print("   3. Refresh dashboard")
    elif not api_running:
        print("⚠️  ACTION REQUIRED: Backend not running")
        print("\n🎯 Next Steps:")
        print("   1. Start backend: cd backend && uvicorn app.main:app --reload")
        print("   2. Verify API: http://localhost:8000/api/opportunities")
        print("   3. Start frontend: cd frontend && npm run dev")
    
except Exception as e:
    print(f"❌ Error generating summary: {e}")

print("="*70 + "\n")
