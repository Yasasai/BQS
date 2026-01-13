
import requests
import os
import json
import logging
import sys

# Log to File
LOG_FILE = os.path.join(os.path.dirname(__file__), 'debug_log.txt')
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO, 
    format='%(asctime)s - %(message)s',
    filemode='w'
)
logger = logging.getLogger(__name__)

# Also print to stdout just in case
console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.INFO)
logger.addHandler(console)

# Oracle CRM Configuration
BASE_URL = os.getenv('ORACLE_BASE_URL', 'https://eijs-test.fa.em2.oraclecloud.com')
USERNAME = os.getenv('ORACLE_USERNAME', 'yasasvi.upadrasta@inspiraenterprise.com')
PASSWORD = os.getenv('ORACLE_PASSWORD', 'Welcome@123')

# Specific Resource ID requested by user
TARGET_ID = '1602737'

def debug_access():
    logger.info("="*60)
    logger.info(f"🔍 ORACLE API DEBUGGER - STARTING")
    logger.info("="*60)
    logger.info(f"Testing access for ID: {TARGET_ID}")
    
    # 1. Try Direct Access
    direct_url = f"{BASE_URL}/crmRestApi/resources/latest/opportunities/{TARGET_ID}"
    logger.info(f"\n[Attempt 1] Direct Access Request...")
    logger.info(f"URL: {direct_url}")
    
    try:
        response = requests.get(direct_url, auth=(USERNAME, PASSWORD), timeout=15)
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            logger.info("✅ SUCCESS: Found resource by Direct ID.")
            log_details(response.json())
            return
        elif response.status_code == 404:
            logger.info("❌ 404 Not Found. Checking if it's an OptyNumber...")
        else:
            logger.info(f"❌ Failed with status {response.status_code}")
            logger.info(f"Response: {response.text[:200]}")

    except Exception as e:
        logger.info(f"❌ Connection Error: {e}")

    # 2. Try Search by OptyNumber
    logger.info(f"\n[Attempt 2] Search by OptyNumber...")
    search_url = f"{BASE_URL}/crmRestApi/resources/latest/opportunities"
    params = {
        'q': f'OptyNumber={TARGET_ID}',
        'fields': 'OptyId,OptyNumber,Name,Revenue,SalesStage'
    }
    logger.info(f"URL: {search_url}?q={params['q']}")
    
    try:
        response = requests.get(search_url, params=params, auth=(USERNAME, PASSWORD), timeout=15)
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            if items:
                logger.info(f"✅ SUCCESS: Found {len(items)} record(s) by OptyNumber.")
                log_details(items[0])
            else:
                logger.info("❌ Returns 200 OK but 'items' list is empty. ID does not exist as OptyNumber either.")
        else:
            logger.info(f"❌ Search failed with status {response.status_code}")

    except Exception as e:
        logger.info(f"❌ Connection Error: {e}")

def log_details(data):
    logger.info("\n--- Record Details ---")
    logger.info(json.dumps(data, indent=2))

if __name__ == "__main__":
    debug_access()
