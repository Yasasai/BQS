
import requests
import sys
import json
import uuid

BASE_URL = "http://127.0.0.1:8000/api"

def print_result(name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {name}")
    if details:
        print(f"   Details: {details}")
    if not passed:
        sys.exit(1)

def verify_pagination():
    print("\n--- Verifying Pagination ---")
    
    # 1. Fetch Page 1, Limit 5
    res1 = requests.get(f"{BASE_URL}/opportunities/?page=1&limit=5")
    if res1.status_code != 200:
        print_result("Fetch Page 1", False, f"Status: {res1.status_code}")
        return

    data1 = res1.json()
    if "items" not in data1 or "total_count" not in data1:
        print_result("Response Structure", False, f"Keys: {data1.keys()}")
        return
    
    items1 = data1["items"]
    print_result("Response Structure", True, f"Found {len(items1)} items, Total: {data1['total_count']}")
    
    if len(items1) > 5:
        print_result("Limit Check", False, f"Expected <= 5, got {len(items1)}")
        return
    
    # 2. Fetch Page 2
    res2 = requests.get(f"{BASE_URL}/opportunities/?page=2&limit=5")
    items2 = res2.json().get("items", [])
    
    # Check if items are different (assuming enough data)
    if len(items1) > 0 and len(items2) > 0:
        is_different = items1[0]['id'] != items2[0]['id']
        print_result("Pagination Offset", is_different, f"Page 1 Item[0]: {items1[0]['id']}, Page 2 Item[0]: {items2[0]['id']}")
    else:
        print("   ⚠️ Not enough data to verify offset difference")

def verify_user_management():
    print("\n--- Verifying User Management ---")
    
    test_email = f"test_sa_{uuid.uuid4().hex[:8]}@example.com"
    test_name = "Test Solution Architect"
    
    # 1. Create User
    payload = {
        "email": test_email,
        "display_name": test_name,
        "roles": ["SA"]
    }
    res_create = requests.post(f"{BASE_URL}/users/", json=payload)
    
    if res_create.status_code != 200:
        print_result("Create User", False, f"Status: {res_create.status_code}, Body: {res_create.text}")
        return
    
    user_data = res_create.json()
    new_user_id = user_data["user_id"]
    print_result("Create User", True, f"Created ID: {new_user_id}")

    # 2. List Users
    res_list = requests.get(f"{BASE_URL}/users/")
    users = res_list.json()
    found = any(u['user_id'] == new_user_id for u in users)
    print_result("List Users", found, "Newly created user found in list")
    
    # 3. Update User
    update_payload = {"display_name": "Updated Name"}
    res_update = requests.put(f"{BASE_URL}/users/{new_user_id}", json=update_payload)
    if res_update.status_code == 200 and res_update.json()["display_name"] == "Updated Name":
        print_result("Update User", True, "Display name updated")
    else:
        print_result("Update User", False, f"Status: {res_update.status_code}")

if __name__ == "__main__":
    try:
        verify_pagination()
        verify_user_management()
        print("\n🎉 All verifications passed!")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Is it running on port 8000?")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
