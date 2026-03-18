import os
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Generator, Optional
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

# Global constants for Oracle CRM REST API
# These can be overridden in the constructor or via environment variables
DEFAULT_BASE_URL = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")
DEFAULT_USER = os.getenv("ORACLE_USER")
DEFAULT_PASS = os.getenv("ORACLE_PASSWORD", os.getenv("ORACLE_PASS"))
API_VERSION = os.getenv("ORACLE_API_VERSION", "latest")

# Setup logger
logger = logging.getLogger(__name__)

class OracleCRMClient:
    """
    Oracle CRM REST API Client Foundation.
    Handles authentication, retries with exponential backoff, and pagination.
    """
    
    def __init__(
        self, 
        base_url: Optional[str] = None, 
        user: Optional[str] = None, 
        password: Optional[str] = None
    ):
        """
        Initializes the Oracle CRM Client.
        
        Args:
            base_url: The root URL of the Oracle instance.
            user: Username for Basic Auth.
            password: Password for Basic Auth.
        """
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.user = user or DEFAULT_USER
        self.password = password or DEFAULT_PASS
        
        # Construct the REST Root URL
        self.rest_root = f"{self.base_url}/crmRestApi/resources/{API_VERSION}"
        
        if not self.user or not self.password:
            logger.warning("Oracle CRM Client initialized without full credentials. API calls may fail.")

        self.session = requests.Session()
        self.session.auth = (self.user, self.password)
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "REST-Framework-Version": "1" # Use standard Oracle REST framework
        })

        # Task 1: Exponential Backoff Configuration
        # 3 retries at 5s, 15s, 45s
        self.max_retries = 3
        self.backoff_steps = [5, 15, 45]

    def _execute_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Executes an HTTP request with exponential backoff and transient error handling.
        
        Task 1: Exponential backoff for transient failures (429, 5xx, timeouts).
        Do not retry on permanent errors (400, 401, 403, 404).
        """
        logger.info("STAGE 2: Entering Oracle API extractor function.")
        logger.info(f"STAGE 2b: Config Check - URL: {os.getenv('ORACLE_BASE_URL')} | USER: {os.getenv('ORACLE_USER')}")
        
        url = f"{self.rest_root}/{endpoint.lstrip('/')}"
        params = kwargs.get('params')
        
        for attempt in range(self.max_retries + 1):
            try:
                # Set a reasonable timeout for the request itself
                logger.info(f"STAGE 3: Making HTTP GET to: {url} with params: {params}")
                response = self.session.request(method, url, timeout=60, **kwargs)
                
                logger.info(f"STAGE 4: Received HTTP {response.status_code} from Oracle.")
                
                # Success path
                if response.ok:
                    return response.json()

                status_code = response.status_code
                
                # Permanent Errors: Do not retry
                if status_code in [400, 401, 403, 404]:
                    logger.error(f"Permanent Oracle API error {status_code} for {url}: {response.text}")
                    response.raise_for_status()

                # Transient Failures: Retry on 429 (Rate Limit) or 5xx (Server Error)
                if status_code == 429 or 500 <= status_code < 600:
                    if attempt < self.max_retries:
                        delay = self.backoff_steps[attempt]
                        logger.warning(
                            f"Transient error {status_code}. Retrying in {delay}s... "
                            f"(Attempt {attempt + 1}/{self.max_retries})"
                        )
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(f"Max retries reached for {url} with status {status_code}")
                        response.raise_for_status()

                # Catch-all for other non-ok responses
                response.raise_for_status()

            except (Timeout, ConnectionError) as e:
                # Transient network-level failures
                if attempt < self.max_retries:
                    delay = self.backoff_steps[attempt]
                    logger.warning(
                        f"Network error ({type(e).__name__}) for {url}. "
                        f"Retrying in {delay}s... (Attempt {attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"Network error after {self.max_retries} retries: {e}")
                    raise
            except RequestException as e:
                # Other request errors (e.g. invalid URL) are usually not retried
                logger.error(f"Oracle API Request failed: {e}")
                raise

        return {}

    def fetch_opportunities(
        self, 
        watermark_from_ts: datetime, 
        watermark_to_ts: datetime, 
        page_size: int = 100
    ) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Task 2: Implement Opportunity Pagination (Stage B)
        Fetches 'OPEN' opportunities modified within the watermark range.
        
        Args:
            watermark_from_ts: Start timestamp (exclusive)
            watermark_to_ts: End timestamp (inclusive)
            page_size: Number of records per page
            
        Yields:
            List of opportunity dictionaries per page.
        """
        offset = 0
        
        # Oracle REST API 'q' parameter date format (YYYY-MM-DD HH:MM:SS)
        from_str = watermark_from_ts.strftime("%Y-%m-%d %H:%M:%S")
        to_str = watermark_to_ts.strftime("%Y-%m-%d %H:%M:%S")

        # Business Filter: StatusCode='OPEN'
        # Technical Watermark Filter: LastUpdateDate range
        query = f"StatusCode='OPEN' AND LastUpdateDate > '{from_str}' AND LastUpdateDate <= '{to_str}'"
        
        while True:
            params = {
                "q": query,
                "limit": page_size,
                "offset": offset,
                "onlyData": "true" # Fetch only raw data, omit links for performance
            }
            
            logger.info(f"Fetching opportunities at offset {offset} (batch size: {page_size})")
            data = self._execute_request("GET", "opportunities", params=params)
            
            items = data.get("items", [])
            logger.info(f"Oracle API returned {len(items)} items in the current page.")
            if not items:
                break
                
            yield items
            
            # Pagination Logic: Stop if we fetched less than the limit or 'hasMore' is false
            if len(items) < page_size or not data.get("hasMore", False):
                break
                
            offset += page_size

    def fetch_opportunity_resources(self, opty_number: str) -> List[Dict[str, Any]]:
        """
        Task 3: Implement Resource Fetching (Stage E)
        Calls child resource endpoint for a specific opportunity using its OptyNumber.
        
        Args:
            opty_number: The business identifier for the opportunity (OptyNumber).
            
        Returns:
            List of resource dictionaries (team members, etc.)
        """
        # Per requirements: Strictly call using opty_number, NOT the internal OptyId.
        endpoint = f"opportunities/{opty_number}/child/OpportunityResource"
        
        logger.info(f"Fetching resources for Opportunity Number: {opty_number}")
        data = self._execute_request("GET", endpoint)
        
        return data.get("items", [])
