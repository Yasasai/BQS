import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.auth import HTTPBasicAuth
import logging
import os
import base64
from datetime import datetime
from dotenv import load_dotenv

# Load env with absolute path to ensure it's found
# .../BQS/backend/app/services/oracle_service.py -> .../BQS/.env
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
env_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path=env_path)

# Configuration
ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")
ORACLE_API_VERSION = os.getenv("ORACLE_API_VERSION", "latest")  # Can be 'latest' or specific like '11.12.1.0'
ORACLE_TOKEN_URL = os.getenv("ORACLE_TOKEN_URL")
ORACLE_CLIENT_ID = os.getenv("ORACLE_CLIENT_ID")
ORACLE_CLIENT_SECRET = os.getenv("ORACLE_CLIENT_SECRET")
ORACLE_SCOPE = os.getenv("ORACLE_SCOPE", f"{ORACLE_BASE_URL}/crmRestApi/resources/{ORACLE_API_VERSION}/")

# Fallback to Basic Auth
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASS = os.getenv("ORACLE_PASSWORD", os.getenv("ORACLE_PASS"))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_robust_session():
    """Returns a requests Session with built-in retries and timeouts"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def get_oracle_token():
    """Retrieves OAuth2 access token for Oracle CRM"""
    if not all([ORACLE_TOKEN_URL, ORACLE_CLIENT_ID, ORACLE_CLIENT_SECRET]):
        return None

    try:
        auth_str = f"{ORACLE_CLIENT_ID}:{ORACLE_CLIENT_SECRET}"
        encoded_auth = base64.b64encode(auth_str.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        payload = {
            "grant_type": "client_credentials",
            "scope": ORACLE_SCOPE
        }
        
        session = get_robust_session()
        response = session.post(ORACLE_TOKEN_URL, headers=headers, data=payload, timeout=30)
        response.raise_for_status()
        
        return response.json().get("access_token")
    except Exception as e:
        logger.error(f"Failed to acquire Oracle token: {e}")
        return None

def get_from_oracle(endpoint, params=None):
    """Generic Oracle API Caller with Bearer token and robust session"""
    token = get_oracle_token()
    url = f"{ORACLE_BASE_URL}/crmRestApi/resources/{ORACLE_API_VERSION}/{endpoint}"
    
    headers = {"Content-Type": "application/json"}
    auth = None

    if token:
        headers["Authorization"] = f"Bearer {token}"
    elif ORACLE_USER and ORACLE_PASS:
        auth = HTTPBasicAuth(ORACLE_USER, ORACLE_PASS)
    else:
        raise Exception("No Oracle credentials found.")

    try:
        session = get_robust_session()
        
        # DEBUG: Show the complete URL with parameters
        from urllib.parse import urlencode
        if params:
            debug_url = f"{url}?{urlencode(params)}"
            logger.info(f"📡 API Request: GET {debug_url}")
        else:
            logger.info(f"📡 API Request: GET {url}")
        
        response = session.get(url, headers=headers, auth=auth, params=params, timeout=90)
        
        # DEBUG: Log Status and Raw Body
        logger.info(f"💾 Response Status: {response.status_code}")
        
        # Log the actual URL that was called
        logger.info(f"🔗 Actual URL: {response.url}")
        
        try:
            raw_data = response.json()
            # Log a small preview of the keys to avoid terminal bloat
            logger.info(f"📦 Response Keys: {list(raw_data.keys())}")
            
            # If we have items, show count
            if "items" in raw_data:
                logger.info(f"📊 Items in response: {len(raw_data.get('items', []))}")
        except:
            logger.info(f"📄 Raw Body (first 500 chars): {response.text[:500]}")

        if response.status_code in [401, 403]:
            return {"error": "Authentication failed", "status": response.status_code}
            
        if not response.ok:
            logger.error(f"❌ Oracle API Error ({response.status_code}): {response.text}")
            return {"error": response.text, "status": response.status_code}

        return response.json()
    except Exception as e:
        logger.error(f"❌ Oracle API call failed ({endpoint}): {e}")
        return {"error": str(e)}

def get_auth_header():
    """Helper to return the correct Authorization header"""
    token = get_oracle_token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    elif ORACLE_USER and ORACLE_PASS:
        auth_str = f"{ORACLE_USER}:{ORACLE_PASS}"
        encoded_auth = base64.b64encode(auth_str.encode()).decode()
        return {"Authorization": f"Basic {encoded_auth}"}
    return {}

def get_all_opportunities(batch_size=50, since_date=None):
    """
    Batch Opportunity Fetching using Oracle Finder API
    
    Uses MyOpportunitiesFinder with ALLOPTIES RecordSet to fetch all opportunities.
    This matches the Oracle URL format:
    /opportunities?finder=MyOpportunitiesFinder;RecordSet='ALLOPTIES'
    
    Args:
        batch_size: Number of records per batch (default 50)
        since_date: ISO date string for incremental sync (optional)
    
    Yields:
        List of opportunity dictionaries from Oracle
    """
    
    offset = 0
    total_count = 0
    MAX_RECORDS = 10000
    
    logger.info(f"🚀 Starting Oracle sync using MyOpportunitiesFinder (Batch size: {batch_size})")
    
    while total_count < MAX_RECORDS:
        # Oracle requires BOTH finder and q parameters for complete results
        # - finder: Specifies which finder to use (MyOpportunitiesFinder)
        # - q: Query filter to get ALL records (RecordSet='ALL')
        params = {
            "finder": "MyOpportunitiesFinder;RecordSet='ALLOPTIES'",
            "q": "RecordSet='ALL'",  # ← CRITICAL: Forces Oracle to return ALL opportunities
            "onlyData": "true",
            "totalResults": "true",  # ← Helps with pagination
            "limit": batch_size,
            "offset": offset
        }
        
        # Add incremental sync filter if date provided
        if since_date:
            oracle_date = since_date.replace('T', ' ')
            # Add date filter to the q parameter
            params["q"] += f";LastUpdateDate > '{oracle_date}'"
            logger.info(f"📅 Incremental sync from: {oracle_date}")
        else:
            logger.info(f"📊 Full sync mode - fetching all opportunities")
        
        # Make API call
        data = get_from_oracle("opportunities", params=params)
        
        # Check for errors
        if "error" in data: 
            logger.error(f"🛑 Sync halted due to API error: {data['error']}")
            break
            
        items = data.get("items", [])
        
        # Log results
        if "items" not in data and offset == 0:
             logger.warning(f"⚠️  Key 'items' missing. Response keys: {list(data.keys())}")
        else:
             logger.info(f"✅ Batch {offset//batch_size + 1}: Found {len(items)} opportunities")
            
        # No more items
        if not items: 
            logger.info(f"✓ Sync complete. Total opportunities fetched: {total_count}")
            break
            
        total_count += len(items)
        yield items
        
        # Check if more pages exist
        if not data.get("hasMore", False): 
            logger.info(f"✓ Reached end of data. Total: {total_count} opportunities")
            break
            
        offset += batch_size
        logger.info(f"→ Fetching next batch (offset: {offset})...")

def fetch_single_opportunity(identifier):
    """
    Deep Fetch for specific OptyNumber, OptyId, or Name using Finder API
    
    Args:
        identifier: OptyNumber, OptyId, or Name to search for
    
    Returns:
        Single opportunity dict or None
    """
    # Use MyOpportunitiesFinder with ALLOPTIES and specific ID filter
    # Also include q parameter to ensure we search ALL records
    finder = f"MyOpportunitiesFinder;RecordSet='ALLOPTIES'"
    query = f"RecordSet='ALL';(OptyNumber = '{identifier}' OR OptyId = '{identifier}' OR Name = '{identifier}')"
    params = {
        "finder": finder,
        "q": query,  # ← CRITICAL: Search in ALL opportunities
        "onlyData": "true",
        "limit": 1
    }
    
    logger.info(f"🔍 Searching for opportunity: {identifier}")
    data = get_from_oracle("opportunities", params=params)
    items = data.get("items", [])
    
    if items:
        logger.info(f"✓ Found opportunity: {items[0].get('Name', identifier)}")
    else:
        logger.warning(f"⚠️  Opportunity not found: {identifier}")
    
    return items[0] if items else None

def fetch_opportunity_by_name(name):
    """
    Specific search by Name for UI-interlinking using Finder API
    
    Args:
        name: Opportunity name to search for
    
    Returns:
        Single opportunity dict or None
    """
    # Use MyOpportunitiesFinder with q parameter for ALL records
    finder = f"MyOpportunitiesFinder;RecordSet='ALLOPTIES'"
    query = f"RecordSet='ALL';Name = '{name}'"
    params = {
        "finder": finder,
        "q": query,  # ← CRITICAL: Search in ALL opportunities
        "onlyData": "true",
        "limit": 1
    }
    
    logger.info(f"🔍 Searching for opportunity by name: {name}")
    data = get_from_oracle("opportunities", params=params)
    items = data.get("items", [])
    
    if items:
        logger.info(f"✓ Found opportunity: {items[0].get('OptyNumber', 'N/A')}")
    else:
        logger.warning(f"⚠️  Opportunity not found by name: {name}")
    
    return items[0] if items else None
