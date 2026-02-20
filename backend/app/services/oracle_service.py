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
            logger.info(f"API Request: GET {debug_url}")
        else:
            logger.info(f"API Request: GET {url}")
        
        response = session.get(url, headers=headers, auth=auth, params=params, timeout=90)
        
        # DEBUG: Log Status and Raw Body
        logger.info(f"Response Status: {response.status_code}")
        
        # Log the actual URL that was called
        logger.info(f"Actual URL: {response.url}")
        
        try:
            raw_data = response.json()
            # Log a small preview of the keys to avoid terminal bloat
            logger.info(f"Response Keys: {list(raw_data.keys())}")
            
            # If we have items, show count
            if "items" in raw_data:
                logger.info(f"Items in response: {len(raw_data.get('items', []))}")
        except:
            logger.info(f"📄 Raw Body (first 500 chars): {response.text[:500]}")

        if response.status_code in [401, 403]:
            return {"error": "Authentication failed", "status": response.status_code}
            
        if not response.ok:
            logger.error(f"Oracle API Error ({response.status_code}): {response.text}")
            return {"error": response.text, "status": response.status_code}

        return response.json()
    except Exception as e:
        logger.error(f"Oracle API call failed ({endpoint}): {e}")
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
    Batch Opportunity Fetching using Oracle Finder API.
    Refactored to avoid 400 Bad Request by separating total count check from data fetch.
    """
    
    offset = 0
    total_count = 0
    MAX_RECORDS = 10000
    
    logger.info(f"Starting Oracle sync using MyOpportunitiesFinder (Batch size: {batch_size})")
    
    # Optional: Get total count first if needed, but for iteration we can just check 'hasMore'
    # The previous implementation mixed totalResults=true with other params which caused 400.
    
    while total_count < MAX_RECORDS:
        # Simplified query known to work in this environment
        params = {
            "q": "StatusCode='OPEN'",  
            "onlyData": "true",
            "limit": batch_size,
            "offset": offset
        }
        
        # Add incremental sync filter if date provided
        if since_date:
            oracle_date = since_date.replace('T', ' ')
            params["q"] += f" AND LastUpdateDate > '{oracle_date}'"
            logger.info(f"Incremental sync from: {oracle_date}")
        else:
            logger.info(f"Full sync mode (StatusCode='OPEN')")
        
        # Make API call
        data = get_from_oracle("opportunities", params=params)
        
        # Check for errors
        if "error" in data: 
            logger.error(f"Sync halted due to API error: {data['error']}")
            break
            
        items = data.get("items", [])
        
        # Log results
        if "items" not in data and offset == 0:
             logger.warning(f"Key 'items' missing. Response keys: {list(data.keys())}")
        else:
             logger.info(f"Batch {offset//batch_size + 1}: Found {len(items)} opportunities")
            
        # No more items
        if not items: 
            logger.info(f"Sync complete. Total opportunities fetched: {total_count}")
            break
            
        total_count += len(items)
        yield items
        
        # Check if more pages exist
        if not data.get("hasMore", False): 
            logger.info(f"Reached end of data. Total: {total_count} opportunities")
            break
            
        offset += batch_size
        logger.info(f"→ Fetching next batch (offset: {offset})...")


def fetch_single_opportunity(identifier):
    """Deep Fetch for specific OptyNumber, OptyId, or Name"""
    finder = f"MyOpportunitiesFinder;RecordSet='ALLOPTIES'"
    query = f"RecordSet='ALL';(OptyNumber = '{identifier}' OR OptyId = '{identifier}' OR Name = '{identifier}')"
    params = {"finder": finder, "q": query, "onlyData": "true", "limit": 1}
    data = get_from_oracle("opportunities", params=params)
    items = data.get("items", [])
    return items[0] if items else None

def fetch_opportunity_by_name(name):
    """Specific search by Name for UI-interlinking"""
    finder = f"MyOpportunitiesFinder;RecordSet='ALLOPTIES'"
    query = f"RecordSet='ALL';Name = '{name}'"
    params = {"finder": finder, "q": query, "onlyData": "true", "limit": 1}
    data = get_from_oracle("opportunities", params=params)
    items = data.get("items", [])
    return items[0] if items else None

def map_oracle_to_db(item):
    """
    Robustly map Oracle JSON to our internal database model.
    Addresses Hint #3: Logs errors instead of silent failure.
    """
    try:
        opty_id = str(item.get("OptyId"))
        if not opty_id:
            logger.warning(f"Item missing OptyId: {item.get('Name')}")
            return None
        
        # Parse Dates
        def parse_date(date_str):
            if not date_str: return None
            try:
                # Handle Oracle Z and +00:00 formats
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                return None

        last_update_str = item.get("LastUpdateDate") or item.get("OptyLastUpdateDate")
        crm_last_updated_at = parse_date(last_update_str) or datetime.utcnow()
        
        close_date = None
        eff_date = item.get("EffectiveDate")
        if eff_date:
            try:
                # Oracle dates often have T00:00:00.000+00:00
                close_date = datetime.strptime(eff_date[:10], "%Y-%m-%d")
            except: pass

        return {
            "opp_id": opty_id,
            "opp_number": str(item.get("OptyNumber") or opty_id),
            "opp_name": item.get("Name") or "Unknown Opportunity",
            "customer_name": item.get("TargetPartyName") or "Unknown Account",
            "geo": item.get("GEO_c") or item.get("Geo_c") or "Global",
            "currency": item.get("CurrencyCode", "USD"),
            "deal_value": float(item.get("Revenue") or 0),
            "stage": item.get("SalesStage"),
            "close_date": close_date,
            "crm_last_updated_at": crm_last_updated_at,
            "practice_name_temp": item.get("Practice_c"), # Internal temp field for practice resolution
            "is_active": True
        }
    except Exception as e:
        logger.error(f"Mapping Error for {item.get('OptyId', 'Unknown')}: {e}")
        return None

def sync_opportunities_to_db(db_session=None):
    """
    Core sync high-level implementation.
    Addresses Hint #1 (Batch Commit), Hint #2 (JSON Item Parsing), Hint #3 (Logging).
    """
    from backend.app.core.database import SessionLocal
    from backend.app.models import Opportunity, Practice, SyncMeta
    import uuid

    db = db_session or SessionLocal()
    total_processed = 0
    total_saved = 0
    start_time = datetime.utcnow()

    logger.info("Starting robust synchronization...")

    try:
        # Loop through batches yielded by get_all_opportunities
        # Note: get_all_opportunities already implements Hint #2 (items = data.get('items', []))
        for batch in get_all_opportunities(batch_size=50):
            batch_objects = []
            
            for item in batch:
                mapped_data = map_oracle_to_db(item)
                if not mapped_data:
                    continue
                
                total_processed += 1
                
                # 1. Resolve Practice (Side Effect but needed)
                practice_val = mapped_data.pop("practice_name_temp")
                if practice_val:
                    practice = db.query(Practice).filter(Practice.practice_name == practice_val).first()
                    if not practice:
                        practice = Practice(
                            practice_id=str(uuid.uuid4()),
                            practice_code=practice_val.upper().replace(" ", "_")[:20],
                            practice_name=practice_val
                        )
                        db.add(practice)
                        db.flush() # Ensure ID generated but don't commit yet
                    mapped_data["primary_practice_id"] = practice.practice_id

                # 2. Upsert Opportunity
                existing = db.query(Opportunity).filter(Opportunity.opp_id == mapped_data["opp_id"]).first()
                if existing:
                    for key, value in mapped_data.items():
                        setattr(existing, key, value)
                else:
                    db.add(Opportunity(**mapped_data))
                
                total_saved += 1
            
            # --- Hint #1: COMMIT AFTER THE BATCH LOOP ---
            try:
                db.commit()
                logger.info(f"Committed batch of {len(batch)} items. Total saved: {total_saved}")
            except Exception as e:
                db.rollback()
                logger.error(f"Batch commit FAILED: {e}. Attempting to salvage next batch.")

        # Final Update to SyncMeta
        meta = db.query(SyncMeta).filter(SyncMeta.meta_key == "oracle_sync_v2").first()
        if not meta:
            meta = SyncMeta(meta_key="oracle_sync_v2")
            db.add(meta)
        meta.last_sync_timestamp = datetime.utcnow()
        meta.sync_status = "SUCCESS"
        meta.records_processed = total_saved
        db.commit()
        
    except Exception as e:
        logger.error(f"CRITICAL SYNC FAILURE: {e}")
        db.rollback()
    finally:
        if not db_session:
            db.close()
            
    duration = (datetime.utcnow() - start_time).total_seconds()
    logger.info(f"Sync Complete! Processed: {total_processed}, Saved: {total_saved} in {duration:.2f}s")
    return {"processed": total_processed, "saved": total_saved}

if __name__ == "__main__":
    # Test run
    sync_opportunities_to_db()
