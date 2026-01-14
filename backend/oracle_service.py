import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.auth import HTTPBasicAuth
import logging
import os
import base64
from datetime import datetime
from dotenv import load_dotenv

# Load env with absolute path to ensure it's found when starting from any directory
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path=env_path)

# Configuration
ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")
ORACLE_TOKEN_URL = os.getenv("ORACLE_TOKEN_URL")
ORACLE_CLIENT_ID = os.getenv("ORACLE_CLIENT_ID")
ORACLE_CLIENT_SECRET = os.getenv("ORACLE_CLIENT_SECRET")
# API Version switched to 'latest' as per successful direct fetch
ORACLE_SCOPE = os.getenv("ORACLE_SCOPE", f"{ORACLE_BASE_URL}/crmRestApi/resources/latest/")

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
    url = f"{ORACLE_BASE_URL}/crmRestApi/resources/latest/{endpoint}"
    
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
        logger.info(f"📡 API Request: GET {url}")
        response = session.get(url, headers=headers, auth=auth, params=params, timeout=90)
        
        # DEBUG: Log Status and Raw Body
        logger.info(f"💾 Response Status: {response.status_code}")
        try:
            raw_data = response.json()
            # Log a small preview of the keys to avoid terminal bloat
            logger.info(f"📦 Response Keys: {list(raw_data.keys())}")
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

def get_all_opportunities(batch_size=10, since_date=None):
    """Batch Opportunity Fetching (Generator Pattern) - Primary Sync Logic"""
    
    offset = 0
    total_count = 0
    MAX_RECORDS = 10000
    
    logger.info(f"Starting systematic batch fetch (Size: {batch_size})")
    
    while total_count < MAX_RECORDS:
        params = {
            "onlyData": "true",
            "limit": batch_size,
            "offset": offset,
            "q": "RecordSet='ALL'"
        }
        
        if since_date:
            oracle_date = since_date.replace('T', ' ')
            params["q"] += f";LastUpdateDate > '{oracle_date}'"
            print(f"DEBUG: Incremental Sync Query: {params['q']}")
        else:
            print(f"DEBUG: Full Sync Mode (Query: {params['q']})")
        
        data = get_from_oracle("opportunities", params=params)
        
        if "error" in data: 
            logger.error(f"🛑 Sync halted due to API error: {data['error']}")
            break
            
        items = data.get("items", [])
        
        # --- NEW: Aggressive Discovery Logic ---
        if not items and not since_date and offset == 0:
            logger.warning("⚠️  Zero records found. Trying with 'OptyId > 0' filter...")
            params["q"] = "OptyId > 0"
            data = get_from_oracle("opportunities", params=params)
            items = data.get("items", [])
            
            if not items:
                logger.warning("⚠️  Still 0 records. Trying specifically for OptyNumber 1602737...")
                single = fetch_single_opportunity("1602737")
                if single:
                    items = [single]
        # -----------------------------------------
            
        if "items" not in data and offset == 0:
             logger.warning(f"⚠️  Key 'items' missing. Keys: {list(data.keys())}")
        else:
             logger.info(f"✅ Found {len(items)} items in this batch.")
            
        if not items: 
            logger.info("ℹ️  No items returned, ending fetch.")
            break
            
        total_count += len(items)
        yield items
        
        if not data.get("hasMore", False): break
        offset += batch_size

def fetch_single_opportunity(identifier):
    """Deep Fetch for specific OptyNumber, OptyId, or Name"""
    # RecordSet=ALL is critical for visibility across the organization
    q = f"RecordSet='ALL';(OptyNumber = '{identifier}' OR OptyId = '{identifier}' OR Name = '{identifier}')"
    params = {"q": q, "onlyData": "true", "limit": 1}
    
    data = get_from_oracle("opportunities", params=params)
    items = data.get("items", [])
    return items[0] if items else None

def fetch_opportunity_by_name(name):
    """Specific search by Name for UI-interlinking"""
    q = f"RecordSet='ALL';Name = '{name}'"
    params = {"q": q, "onlyData": "true", "limit": 1}
    data = get_from_oracle("opportunities", params=params)
    items = data.get("items", [])
    return items[0] if items else None

def map_oracle_to_db(oracle_item):
    """Map Oracle JSON to BQS model with self-healing field detection"""
    try:
        def get_val(keys, default=None):
            if isinstance(keys, str): keys = [keys]
            for key in keys:
                val = oracle_item.get(key)
                if val is not None: return val
            return default

        def parse_date(date_str):
            if not date_str: return None
            try:
                # Oracle dates often come as 2024-01-13T10:00:00.000+00:00
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                return None

        # OptyNumber is our reference Coordinate
        remote_id = str(get_val(["OptyNumber", "OptyId"]))

        # Construct Opportunity URL
        static_url = f"{ORACLE_BASE_URL}/crmRestApi/resources/latest/opportunities/"
        remote_url = f"{static_url}{remote_id}"

        # Primary Opportunity Model Fields
        primary_data = {
            "remote_id": remote_id,
            "name": get_val(["Name", "OpportunityName"], "Untitled"),
            "customer": get_val(["AccountName", "TargetPartyName", "OrganizationName", "CustomerName_c"], "Unknown"),
            "practice": get_val(["Practice_c", "Practice", "ServiceLine_c", "BusinessUnit_c"], "General"),
            "geo": get_val(["Geo_c", "Geo", "Geography_c", "Territory_c"], "Global"),
            "region": get_val(["Region_c", "Region", "Area_c", "SubRegion_c"], "Global"),
            "sector": get_val(["BusinessUnit_c", "Sector_c", "Vertical_c"], "General"),
            "deal_value": float(get_val(["Revenue", "EstimatedRevenue_c", "DealValue_c", "Amount"], 0)),
            "win_probability": float(get_val(["WinProb", "WinProbability", "Probability"], 0)),
            "currency": get_val(["CurrencyCode", "Currency"], "USD"),
            "stage": get_val(["SalesStage", "StageName", "StatusCode"], "New"),
            "close_date": get_val(["CloseDate", "EstimatedCloseDate"]),
            "description": get_val(["Description", "Comments", "Summary"]),
            "remote_url": remote_url,
            "last_synced_at": datetime.utcnow()
        }

        # Extended Detail Model Fields
        detail_data = {
            "opty_number": remote_id,
            "opty_id": str(get_val("OptyId")),
            "name": get_val(["Name", "OpportunityName"]),
            "account_name": get_val(["AccountName", "TargetPartyName", "OrganizationName"]),
            "revenue": float(get_val(["Revenue", "EstimatedRevenue_c", "Amount"], 0)),
            "currency_code": get_val(["CurrencyCode", "Currency"]),
            "win_probability": float(get_val(["WinProb", "WinProbability", "Probability"], 0)),
            "practice": get_val(["Practice_c", "Practice", "ServiceLine_c"]),
            "geo": get_val(["Geo_c", "Geo", "Geography_c"]),
            "region": get_val(["Region_c", "Region", "Area_c"]),
            "business_unit": get_val(["BusinessUnit_c", "BU_c"]),
            "customer_sponsor": get_val(["CustomerSponsor_c", "Sponsor_c"]),
            "primary_partner": get_val(["PrimaryPartnerOrgPartyName", "PartnerName_c"]),
            "owner_name": get_val(["OwnerName", "ResourceName"]),
            "primary_contact": get_val(["PrimaryContactPartyName", "ContactName_c"]),
            "sales_stage": get_val(["SalesStage", "StageName"]),
            "sales_method": get_val(["SalesMethod", "MethodName"]),
            "status_code": get_val(["StatusCode", "Status"]),
            "status_label": get_val(["Status", "StatusName"]),
            "close_date": get_val(["CloseDate", "EstimatedCloseDate"]),
            "effective_date": get_val(["EffectiveDate", "CreationDate"]),
            "last_update_date": parse_date(get_val("LastUpdateDate")),
            "creation_date": parse_date(get_val("CreationDate")),
            "description": get_val(["Description", "Summary"]),
            "raw_json": oracle_item,
            "remote_url": remote_url,
            "last_synced_at": datetime.utcnow()
        }

        return {"primary": primary_data, "details": detail_data}

    except Exception as e:
        logger.error(f"Mapping error for {oracle_item.get('OptyNumber')}: {e}")
        return None
