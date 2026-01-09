import requests
from requests.auth import HTTPBasicAuth
import logging
import base64

# Configuration (In production, use .env)
ORACLE_BASE_URL = "https://eijs-test.fa.em2.oraclecloud.com"
ORACLE_USER = "yasasvi.upadrasta@inspiraenterprise.com"
ORACLE_PASS = "Welcome@123"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_oracle_opportunities():
    """
    Fetch opportunities from Oracle CX Sales REST API.
    """
    endpoint = f"{ORACLE_BASE_URL}/crmRestApi/resources/latest/opportunities"
    
    # Fields to select - Adjust based on actual Oracle field names
    # Common fields: OptyId, OptyNumber, Name, TargetPartyName, Revenue, SalesStage, EffectiveDate
    # Custom fields might be needed for 'Practice', 'Geo'.
    fields = "OptyId,OptyNumber,Name,TargetPartyName,Revenue,CurrencyCode,WinProb,SalesStage,EffectiveDate,OwnerResourcePartyId,LastUpdateDate"
    
    params = {
        "fields": fields,
        "onlyData": "true",
        "limit": 100 # Fetch 100 for now. Implement pagination for full sync.
    }
    
    logger.info(f"Fetching opportunities from {endpoint}...")
    
    try:
        response = requests.get(
            endpoint, 
            auth=HTTPBasicAuth(ORACLE_USER, ORACLE_PASS),
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            logger.info(f"Successfully fetched {len(items)} opportunities.")
            return items
        else:
            logger.error(f"Failed to fetch from Oracle. Status: {response.status_code}, Response: {response.text}")
            return []
            
    except Exception as e:
        logger.error(f"Error connecting to Oracle: {e}")
        return []

def map_oracle_to_db(oracle_item):
    """
    Map Oracle API response item to local Opportunity model dict.
    """
    # Defensive coding for missing keys
    return {
        "remote_id": str(oracle_item.get("OptyId")), # Use OptyId as remote key
        "name": oracle_item.get("Name"),
        "customer": oracle_item.get("TargetPartyName"),
        # 'Practice' and 'Geo' might need custom field mapping or lookup. 
        # For now, leaving them null or mapping to generic fields if available.
        "practice": "Unknown", # Needs specific field identification
        "geo": "Unknown",
        "deal_value": oracle_item.get("Revenue", 0),
        "currency": oracle_item.get("CurrencyCode", "USD"), # Fetch actual currency
        "win_probability": oracle_item.get("WinProb", 0), # Map Win Probability
        "sales_owner": str(oracle_item.get("OwnerResourcePartyId")), # Needs name resolution
        "stage": oracle_item.get("SalesStage"),
        # Dates - parse standard ISO format if possible, else handle errors
        "close_date": oracle_item.get("EffectiveDate"), 
        # "last_updated_in_crm": oracle_item.get("LastUpdateDate") # Needs parsing
    }
