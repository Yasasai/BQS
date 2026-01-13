import requests
from requests.auth import HTTPBasicAuth
import json

def test_fetch():
    base_url = "https://eijs-test.fa.em2.oraclecloud.com"
    user = "yasasvi.upadrasta@inspiraenterprise.com"
    password = "Welcome@123"
    opty_number = "1602737"
    
    # Try the user's provided link structure
    url = f"{base_url}/crmRestApi/resources/latest/opportunities/{opty_number}"
    
    print(f"Testing direct fetch from: {url}")
    
    try:
        response = requests.get(
            url,
            auth=HTTPBasicAuth(user, password),
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS!")
            with open('direct_oracle_sample.json', 'w') as f:
                json.dump(data, f, indent=2)
            print("Saved to direct_oracle_sample.json")
        else:
            print(f"Error Content: {response.text[:500]}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_fetch()
