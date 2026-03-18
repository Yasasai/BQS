import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set dev mode to enable bypass
os.environ["VITE_DEV_MODE"] = "true"

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def run_tests():
    email = "sarah.mitchell@inspiraenterprise.com"
    print(f"--- Testing SSO Login for {email} ---")
    sso_token = f"mock_azure_token_{email}"
    response = client.post("/api/auth/sso-login", json={"sso_token": sso_token})
    
    if response.status_code == 200:
        data = response.json()
        token = data["access_token"]
        print("SUCCESS: SSO Login returned token:", token[:20] + "...")
        
        print(f"\n--- Testing /api/auth/me Profile Fetch ---")
        me_response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        print("Status:", me_response.status_code)
        print("Response:", me_response.json())
        
        if me_response.status_code == 200 and "PH" in me_response.json().get("roles", []):
            print("SUCCESS: JWT correctly mapped to DB user and returned PH role.")
        else:
            print("ERROR: Roles missing or user fetch failed.")
    else:
        print("ERROR: SSO Login failed.")
        print("Status:", response.status_code)
        print("Response:", response.text)

if __name__ == "__main__":
    run_tests()
