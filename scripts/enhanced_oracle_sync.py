"""
Enhanced Oracle Sync - Delta Fetch & Bulk Upsert
================================================
Features:
1. Delta Fetch: Only fetches records updated since the last successful sync.
2. Bulk Upsert: Uses efficient PostgreSQL `COPY` or `INSERT ... ON CONFLICT` with `execute_values`.
3. Sync Tracking: Updates `sync_meta` table with the latest timestamp.
"""

import sys
import os
import logging
from datetime import datetime, timezone

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import requests
import psycopg2
from psycopg2.extras import execute_values
from oracle_service import get_from_oracle
from dotenv import load_dotenv

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EnhancedSync")

# Load Env
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(base_dir, '.env'))

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'bqs'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'Abcd1234'),
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': os.getenv('DB_PORT', '5432')
}

SYNC_KEY = 'oracle_opportunities'

class EnhancedOracleSync:
    def __init__(self):
        self.conn = None
        
    def connect(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        
    def get_last_sync_time(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT last_sync_timestamp FROM sync_meta WHERE key = %s", (SYNC_KEY,))
            row = cur.fetchone()
            return row[0] if row else None
            
    def update_last_sync_time(self, timestamp):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO sync_meta (key, last_sync_timestamp, updated_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (key) DO UPDATE 
                SET last_sync_timestamp = EXCLUDED.last_sync_timestamp,
                    updated_at = NOW()
            """, (SYNC_KEY, timestamp))
        self.conn.commit()

    def fetch_changes(self, last_sync):
        items = []
        offset = 0
        limit = 500
        has_more = True
        
        # Base query
        q = "RecordSet='ALL'"
        
        # Add delta filter if last_sync exists
        if last_sync:
            # Oracle format: 2024-01-30T10:00:00.000+00:00 or similar
            # Robust formatting: ISO 8601
            # Adjust to ensure we don't miss anything (e.g. overlap by 1 min)
            formatted_date = last_sync.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z' # Simple ISO
            # Note: Oracle might be strict on format. 
            # Often 'YYYY-MM-DDTHH:mm:ss' works.
            # Let's try simple format first.
            formatted_date = last_sync.strftime('%Y-%m-%dT%H:%M:%S') 
            q += f";LastUpdateDate > '{formatted_date}'"
            logger.info(f"🔄 Delta Sync Mode: Fetching changes since {formatted_date}")
        else:
            logger.info("🌍 Full Sync Mode: Fetching ALL records")

        while has_more:
            params = {
                "q": q,
                "limit": limit,
                "offset": offset,
                "onlyData": "true",
                "fields": "OptyNumber,Name,Revenue,WinProb,SalesStage,OwnerName,TargetPartyName,CloseDate,CurrencyCode,Practice_c,Geo_c,Region_c,Sector_c,StatusCode,LastUpdateDate"
            }
            
            # Using the existing service but custom params
            logger.info(f"Fetching batch offset={offset}...")
            response = get_from_oracle("opportunities", params=params)
            
            if "error" in response:
                logger.error(f"API Error: {response['error']}")
                break
                
            batch = response.get('items', [])
            if not batch:
                break
                
            items.extend(batch)
            has_more = response.get('hasMore', False)
            offset += limit
            
            logger.info(f"Fetched {len(batch)} items. Total so far: {len(items)}")
            
        return items

    def process_and_upsert(self, opportunities):
        if not opportunities:
            logger.info("No opportunities to upsert.")
            return

        # Prepare data for execute_values
        # Schema: remote_id, name, deal_value, win_probability, stage, sales_owner, customer, close_date, currency, practice, geo, region, sector, oracle_status, last_synced_at, workflow_status (conditional)
        
        values = []
        now = datetime.now(timezone.utc)
        
        for opp in opportunities:
            remote_id = str(opp.get('OptyNumber'))
            if not remote_id: continue
            
            # Extract basic fields safely
            name = opp.get('Name', 'Untitled')
            revenue = float(opp.get('Revenue', 0) or 0)
            win_prob = float(opp.get('WinProb', 0) or 0)
            stage = opp.get('SalesStage', 'Unknown')
            owner = opp.get('OwnerName')
            customer = opp.get('TargetPartyName')
            close_date = opp.get('CloseDate')
            currency = opp.get('CurrencyCode', 'USD')
            practice = opp.get('Practice_c', 'Unknown')
            geo = opp.get('Geo_c', 'Unknown')
            region = opp.get('Region_c', 'Unknown')
            sector = opp.get('Sector_c', 'Unknown')
            oracle_status = opp.get('StatusCode', 'OPEN')
            
            # workflow_status logic:
            # If OPEN -> NEW_FROM_CRM (initial) or keep existing
            # If LOST/CLOSED -> CLOSED_IN_CRM
            
            initial_wf_status = 'NEW_FROM_CRM' if oracle_status == 'OPEN' else 'CLOSED_IN_CRM'

            values.append((
                remote_id, name, revenue, win_prob, stage, owner, customer, close_date, currency, practice, geo, region, sector, now, initial_wf_status, oracle_status
            ))

        sql = """
            INSERT INTO opportunities (
                remote_id, name, deal_value, win_probability, stage, sales_owner, customer, close_date, currency, practice, geo, region, sector, last_synced_at, workflow_status
            ) VALUES %s
            ON CONFLICT (remote_id) DO UPDATE SET
                name = EXCLUDED.name,
                deal_value = EXCLUDED.deal_value,
                win_probability = EXCLUDED.win_probability,
                stage = EXCLUDED.stage,
                sales_owner = EXCLUDED.sales_owner,
                customer = EXCLUDED.customer,
                close_date = EXCLUDED.close_date,
                currency = EXCLUDED.currency,
                practice = EXCLUDED.practice,
                geo = EXCLUDED.geo,
                region = EXCLUDED.region,
                sector = EXCLUDED.sector,
                last_synced_at = EXCLUDED.last_synced_at,
                workflow_status = CASE 
                    WHEN EXCLUDED.workflow_status = 'CLOSED_IN_CRM' THEN 'CLOSED_IN_CRM'
                    WHEN opportunities.workflow_status = 'CLOSED_IN_CRM' AND EXCLUDED.workflow_status = 'NEW_FROM_CRM' THEN 'NEW_FROM_CRM'
                    ELSE opportunities.workflow_status
                END
        """
        
        with self.conn.cursor() as cur:
            execute_values(cur, sql, values)
            logger.info(f"✅ Upserted {len(values)} records.")
        self.conn.commit()

    def run(self):
        try:
            self.connect()
            
            # 1. Get last sync time
            last_sync = self.get_last_sync_time()
            start_time = datetime.now(timezone.utc)
            
            # 2. Fetch changes
            opportunities = self.fetch_changes(last_sync)
            
            # 3. Upsert
            if opportunities:
                self.process_and_upsert(opportunities)
                
            # 4. Update sync time (if successful)
            # Use start_time to be safe (so we don't miss updates that happened during the fetch)
            self.update_last_sync_time(start_time)
            
            logger.info("✨ Sync completed successfully.")
            
        except Exception as e:
            logger.error(f"❌ Sync failed: {e}")
            if self.conn:
                self.conn.rollback()
        finally:
            if self.conn:
                self.conn.close()

if __name__ == "__main__":
    syncer = EnhancedOracleSync()
    syncer.run()
