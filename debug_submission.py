
import requests
import json
import uuid

BASE_URL = "http://127.0.0.1:8000/api"

def debug_submit():
    # 1. Get an opportunity or create one if needed (assuming some exist)
    # We'll just fetch all opps to get an ID
    try:
        r = requests.get(f"{BASE_URL}/opportunities/")
        r.raise_for_status()
        items = r.json().get("items", [])
        if not items:
            print("No opportunities found to test with.")
            return
        
        opp_id = items[0]['id']
        print(f"Testing with Opportunity ID: {opp_id}")
        
    except Exception as e:
        print(f"Failed to fetch opportunities: {e}")
        return

    # 2. Get a user
    try:
        r = requests.get(f"{BASE_URL}/auth/users")
        r.raise_for_status()
        users = r.json()
        if not users:
            print("No users found.")
            return
        
        # Pick a user, preferably SA
        user = next((u for u in users if 'SA' in u['roles']), users[0])
        user_id = user['user_id']
        print(f"Testing with User ID: {user_id} ({user['display_name']})")
        
    except Exception as e:
        print(f"Failed to fetch users: {e}")
        return

    # 3. Construct Payload
    payload = {
        "user_id": user_id,
        "sections": [
            {
                "section_code": "STRAT",
                "score": 4.0,
                "notes": "Test Note",
                "selected_reasons": []
            },
            {
                "section_code": "WIN",
                "score": 3.0,
                "notes": "Win prob note",
                "selected_reasons": []
            }
        ],
        "confidence_level": "HIGH",
        "recommendation": "PURSUE",
        "summary_comment": "Automated debug submission test."
    }

    # 4. Attempt Submit
    print("Sending POST request to /submit...")
    try:
        url = f"{BASE_URL}/scoring/{opp_id}/submit"
        r = requests.post(url, json=payload)
        
        print(f"Status Code: {r.status_code}")
        try:
            print("Response Body:", json.dumps(r.json(), indent=2))
        except:
            print("Response Text:", r.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    debug_submit()
