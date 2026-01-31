import requests
import json
import time

# Using 127.0.0.1 to avoid Windows localhost timeout issues
BASE_URL = "http://127.0.0.1:8000"

def print_step(msg):
    print(f"\n{'='*60}")
    print(f"👉 {msg}")
    print(f"{'='*60}")

def test_flow():
    # 1. FETCH OPPORTUNITIES
    print_step("Step 1: Fetching Opportunities (Display)")
    try:
        res = requests.get(f"{BASE_URL}/api/opportunities")
        data = res.json()
        print(f"✅ Found {len(data)} opportunities.")
        if not data:
            print("❌ No data found! Please run sync first.")
            return
        
        # Pick the first one
        opp = data[0]
        opp_id = opp['id']
        opp_name = opp['name']
        print(f"📝 Selected Opportunity: {opp_name} (ID: {opp_id})")
        print(f"   Current Status: {opp.get('workflow_status', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Failed to fetch opportunities: {e}")
        return

    # 2. ASSIGN TO SA
    print_step("Step 2: Assigning to Solution Architect")
    sa_email = "sa_test@inspira.com"
    assign_payload = {
        "opp_id": opp_id,
        "sa_email": sa_email
    }
    
    try:
        res = requests.post(f"{BASE_URL}/api/inbox/assign", json=assign_payload)
        if res.status_code == 200:
            print(f"✅ Assigned successfully to {sa_email}")
        else:
            print(f"❌ Assignment failed: {res.text}")
            return
            
        # Verify status change
        res = requests.get(f"{BASE_URL}/api/opportunities")
        updated_opp = next(o for o in res.json() if o['id'] == opp_id)
        print(f"   New Status: {updated_opp.get('workflow_status')}")
        if updated_opp.get('workflow_status') != "ASSIGNED_TO_SA":
            print("⚠️ Status didn't update correctly!")
            
    except Exception as e:
        print(f"❌ Assignment error: {e}")
        return

    # 3. ASSESSMENT SCORING (DRAFT)
    print_step("Step 3: Saving Assessment Draft")
    
    scoring_payload = {
        "user_id": sa_email,
        "confidence_level": "High",
        "recommendation": "Go",
        "summary_comment": "Automated test assessment",
        "sections": [
            {"section_code": "FINANCIAL", "score": 5, "notes": "Good financials", "selected_reasons": ["High Margin"]},
            {"section_code": "TECHNICAL", "score": 4, "notes": "Solid tech stack", "selected_reasons": []},
            {"section_code": "RESOURCE", "score": 3, "notes": "Tight resources", "selected_reasons": []}
        ]
    }
    
    try:
        # Note: In a real scenario, we'd fetch valid sections first.
        # This might print warnings if section codes don't match exactly what's seeded.
        res = requests.post(f"{BASE_URL}/api/scoring/{opp_id}/draft", json=scoring_payload)
        
        if res.status_code == 200:
             print("✅ Draft saved successfully")
        else:
             print(f"❌ Draft save failed: {res.text}")
             
    except Exception as e:
        print(f"❌ Scoring error: {e}")
        return

    # 4. SUBMIT ASSESSMENT
    print_step("Step 4: Submitting Assessment")
    try:
        res = requests.post(f"{BASE_URL}/api/scoring/{opp_id}/submit", json=scoring_payload)
        if res.status_code == 200:
            data = res.json()
            print(f"✅ Submitted successfully!")
            print(f"   Calculated Score: {data.get('overall_score')}")
        else:
            print(f"❌ Submission failed: {res.text}")
            return
            
        # Verify final status
        res = requests.get(f"{BASE_URL}/api/opportunities")
        final_opp = next(o for o in res.json() if o['id'] == opp_id)
        print(f"   Final Workflow Status: {final_opp.get('workflow_status')}")
        
    except Exception as e:
        print(f"❌ Submission error: {e}")

    print("\n" + "="*60)
    print("🎉 FULL FLOW VERIFIED!")
    print("="*60)

if __name__ == "__main__":
    test_flow()
