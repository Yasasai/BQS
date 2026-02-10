
import os
import requests
import logging
from dotenv import load_dotenv

# Path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Configuration
ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL")
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")

# Setup logging to file
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "probe_log.txt")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO, 
    format='%(asctime)s - %(message)s',
    filemode='w'
)

def log(msg):
    # print(msg) # Avoid stdout if it causes issues
    logging.info(msg)

def probe():
    if not ORACLE_BASE_URL:
        log("❌ ORACLE_BASE_URL not set.")
        return

    url = f"{ORACLE_BASE_URL}/crmRestApi/resources/11.12.1.0/opportunities"
    auth = requests.auth.HTTPBasicAuth(ORACLE_USER, ORACLE_PASSWORD)
    
    # List of queries to try
    queries = [
        "StatusCode='OPEN'",
        "StatusCd='OPEN'",
        "OptyStatus='OPEN'",
        "Status='OPEN'",
        "StsCode='OPEN'",
        "OptySts='OPEN'",
        "Revenue > 0" # Control test
    ]
    
    log(f"📡 Probing {len(queries)} query variations on: {url}...")
    
    for q in queries:
        params = {
            "q": q,
            "limit": 1,
            "fields": "OptyId,Name,StatusCode,StatusCd,Status" 
        }
        try:
            log(f"\n👉 Testing: ?q={q}")
            resp = requests.get(url, params=params, auth=auth, timeout=15)
            
            if resp.status_code == 200:
                log(f"✅ SUCCESS! Query '{q}' is valid.")
                data = resp.json()
                items = data.get("items", [])
                if items:
                    log(f"   Sample Item Keys: {list(items[0].keys())}")
                    # Print values of interest
                    for k in ["StatusCode", "StatusCd", "Status", "OptyStatus"]:
                        if k in items[0]:
                            log(f"   Value of '{k}': {items[0][k]}")
                return 
            else:
                log(f"❌ FAILED ({resp.status_code}): {resp.text[:100]}")
                
        except Exception as e:
            log(f"   Error: {e}")

if __name__ == "__main__":
    probe()
