import requests
from requests.auth import HTTPBasicAuth
import logging
import os
from dotenv import load_dotenv

# Load env in case this is run as standalone script
load_dotenv()

# Configuration
ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASS = os.getenv("ORACLE_PASS")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_oracle_opportunities():
    """
    Fetch opportunities from Oracle CX Sales REST API.
    Returns a list of dictionaries.
    """
    if not ORACLE_USER or not ORACLE_PASS:
        logger.error("Oracle credentials not found in environment variables.")
        return []

    # Endpoint for Opportunities
    endpoint = f"{ORACLE_BASE_URL}/crmRestApi/resources/latest/opportunities"
    
    # Fields to select
    # We fetch key fields to map to our internal BQS Opportunity model
    fields = (
        "OptyId,OptyNumber,Name,TargetPartyName,Revenue,CurrencyCode,"
        "WinProb,SalesStage,EffectiveDate,OwnerResourcePartyId,LastUpdateDate"
    )
    
    # Pagination: For now fetching 500 to catch most. 
    # In a full production system, we would loop through 'hasMore'.
    params = {
        "fields": fields,
        "onlyData": "true",
        "limit": 500,
        "orderBy": "LastUpdateDate:desc" # Fetch most recently updated first
    }
    
    logger.info(f"Fetching opportunities from {endpoint}...")
    
    try:
        response = requests.get(
            endpoint, 
            auth=HTTPBasicAuth(ORACLE_USER, ORACLE_PASS),
            params=params,
            timeout=60 # Increased timeout for reliability
        )
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            logger.info(f"Successfully fetched {len(items)} opportunities from Oracle.")
            return items
        else:
            logger.error(f"Failed to fetch from Oracle. Status: {response.status_code}, Response: {response.text}")
            return []
            
    except requests.exceptions.Timeout:
        logger.error("Oracle API Sync timed out. usage.")
        return []
    except Exception as e:
        logger.error(f"Error connecting to Oracle: {e}")
        return []

def map_oracle_to_db(oracle_item):
    """
    Map Oracle API response item to local Opportunity model dict.
    Ensures safe type conversion.
    """
    try:
        # Safe extraction helpers
        def get_val(key, default=None):
            return oracle_item.get(key) or default

        # Currency / Revenue logic
        revenue = get_val("Revenue")
        deal_value = float(revenue) if revenue is not None else 0.0
        
        # Win Prob logic (Oracle often sends 10, 20... we might start with that)
        win_prob = get_val("WinProb")
        win_probability = float(win_prob) if win_prob is not None else 0.0

        return {
            "remote_id": str(get_val("OptyId")),
            "name": get_val("Name", "Untitled Opportunity"),
            "customer": get_val("TargetPartyName", "Unknown Customer"),
            
            # These might need specific logic later, default to placeholders if missing
            "practice": "General", 
            "geo": "Global",
            
            "deal_value": deal_value,
            "currency": get_val("CurrencyCode", "USD"),
            "win_probability": win_probability,
            
            "sales_owner": str(get_val("OwnerResourcePartyId", "")), 
            "stage": get_val("SalesStage", "New"),
            "close_date": get_val("EffectiveDate"), # Should be ISO string
        }
    except Exception as e:
        logger.error(f"Error mapping item {oracle_item}: {e}")
        return None
