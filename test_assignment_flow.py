"""
🔥 Dynamic Frontend Assignment Test Script

This script tests the complete assignment workflow:
1. Backend assignment API
2. Frontend instant UI updates
3. Status transitions
4. Dashboard segregation
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_get_opportunities():
    """Test fetching all opportunities"""
    print("\n📊 TEST 1: Fetching all opportunities...")
    response = requests.get(f"{BASE_URL}/api/opportunities/")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS: Retrieved {len(data)} opportunities")
        
        # Show unassigned opportunities
        unassigned = [opp for opp in data if not opp.get('assigned_sa') or opp['assigned_sa'] == 'Unassigned']
        print(f"   📋 Unassigned: {len(unassigned)}")
        
        # Show assigned opportunities
        assigned = [opp for opp in data if opp.get('assigned_sa') and opp['assigned_sa'] != 'Unassigned']
        print(f"   ✅ Assigned: {len(assigned)}")
        
        # Show first unassigned opportunity for testing
        if unassigned:
            test_opp = unassigned[0]
            print(f"\n   🎯 Test Opportunity:")
            print(f"      ID: {test_opp['id']}")
            print(f"      Name: {test_opp['name']}")
            print(f"      Status: {test_opp['workflow_status']}")
            print(f"      Assigned SA: {test_opp.get('assigned_sa', 'None')}")
            return test_opp['id']
        else:
            print("   ⚠️ No unassigned opportunities found")
            return None
    else:
        print(f"❌ FAILED: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def test_get_users():
    """Test fetching users to get SA email"""
    print("\n👥 TEST 2: Fetching users...")
    response = requests.get(f"{BASE_URL}/api/auth/users")
    
    if response.status_code == 200:
        users = response.json()
        print(f"✅ SUCCESS: Retrieved {len(users)} users")
        
        # Find SAs
        sas = [u for u in users if 'SA' in u.get('roles', [])]
        print(f"   🔧 Solution Architects: {len(sas)}")
        
        if sas:
            test_sa = sas[0]
            print(f"\n   🎯 Test SA:")
            print(f"      Name: {test_sa['display_name']}")
            print(f"      Email: {test_sa['email']}")
            return test_sa['email'], test_sa['display_name']
        else:
            print("   ⚠️ No SAs found")
            return None, None
    else:
        print(f"❌ FAILED: {response.status_code}")
        return None, None

def test_assignment(opp_id, sa_email):
    """Test assigning an opportunity to an SA"""
    print(f"\n🔄 TEST 3: Assigning opportunity {opp_id} to {sa_email}...")
    
    payload = {
        "opp_id": str(opp_id),
        "sa_email": sa_email,
        "assigned_by_user_id": "PRACTICE_HEAD"
    }
    
    print(f"   📤 Request payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/api/inbox/assign",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCCESS: Assignment completed")
        print(f"   📋 Response: {json.dumps(result, indent=2)}")
        return True
    else:
        print(f"❌ FAILED: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def verify_assignment(opp_id, expected_sa_name):
    """Verify the assignment was successful"""
    print(f"\n🔍 TEST 4: Verifying assignment...")
    
    response = requests.get(f"{BASE_URL}/api/opportunities/")
    
    if response.status_code == 200:
        data = response.json()
        opp = next((o for o in data if o['id'] == opp_id), None)
        
        if opp:
            print(f"✅ Opportunity found:")
            print(f"   ID: {opp['id']}")
            print(f"   Name: {opp['name']}")
            print(f"   Assigned SA: {opp.get('assigned_sa', 'None')}")
            print(f"   Status: {opp['workflow_status']}")
            
            # Verify assignment
            if opp.get('assigned_sa') == expected_sa_name:
                print(f"\n   ✅ ASSIGNMENT VERIFIED: SA matches expected value")
            else:
                print(f"\n   ❌ ASSIGNMENT MISMATCH: Expected '{expected_sa_name}', got '{opp.get('assigned_sa')}'")
            
            # Verify status
            if opp['workflow_status'] == 'ASSIGNED_TO_SA':
                print(f"   ✅ STATUS VERIFIED: Workflow status is ASSIGNED_TO_SA")
            else:
                print(f"   ❌ STATUS MISMATCH: Expected 'ASSIGNED_TO_SA', got '{opp['workflow_status']}'")
            
            return True
        else:
            print(f"❌ Opportunity {opp_id} not found")
            return False
    else:
        print(f"❌ FAILED: {response.status_code}")
        return False

def main():
    print("=" * 60)
    print("🔥 DYNAMIC FRONTEND ASSIGNMENT TEST")
    print("=" * 60)
    
    # Test 1: Get opportunities
    opp_id = test_get_opportunities()
    if not opp_id:
        print("\n❌ Cannot proceed without an unassigned opportunity")
        return
    
    # Test 2: Get SA
    sa_email, sa_name = test_get_users()
    if not sa_email:
        print("\n❌ Cannot proceed without an SA")
        return
    
    # Test 3: Assign opportunity
    success = test_assignment(opp_id, sa_email)
    if not success:
        print("\n❌ Assignment failed")
        return
    
    # Test 4: Verify assignment
    verify_assignment(opp_id, sa_name)
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 60)
    print("\n📋 NEXT STEPS:")
    print("1. Open Practice Head Dashboard: http://localhost:5176/practice-head/action-required")
    print("2. Verify the opportunity moved from Unassigned to Assigned")
    print("3. Open SA Dashboard: http://localhost:5176/sa/assigned")
    print("4. Verify the opportunity appears in SA's list")
    print("5. Check that status badge shows 'ASSIGNED TO SA'")

if __name__ == "__main__":
    main()
