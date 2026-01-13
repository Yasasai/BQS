
import os
import sys
import httpx
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from oracle_service import get_auth_header

auth = get_auth_header()
base_url = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")
url = f"{base_url}/crmRestApi/resources/latest/opportunities/1602737"

print(f"Testing URL: {url}")
try:
    with httpx.Client(headers=auth) as client:
        resp = client.get(url)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Name: {resp.json().get('Name')}")
        else:
            print(f"Error: {resp.text[:200]}")
except Exception as e:
    print(f"Exception: {e}")
