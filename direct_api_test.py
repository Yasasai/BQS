import requests
from requests.auth import HTTPBasicAuth
import json

url = "https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/latest/opportunities"
user = "yasasvi.upadrasta@inspiraenterprise.com"
pw = "Welcome@123"

print(f"Testing direct fetch for {user}...")
try:
    search_opty = "1602737"
    params = {"q": f"OptyNumber='{search_opty}'", "onlyData": "true"}
    r = requests.get(url, auth=HTTPBasicAuth(user, pw), params=params, timeout=30)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        items = data.get("items", [])
        print(f"Count: {len(items)}")
        if items:
            print("Success! Data found.")
            print(json.dumps(items[0], indent=2))
        else:
            print(f"API returned 200 but ZERO items for Opty {search_opty}.")
            print("Response:", json.dumps(data, indent=2))
    else:
        print(f"Failed: {r.text}")
except Exception as e:
    print(f"Error: {e}")
