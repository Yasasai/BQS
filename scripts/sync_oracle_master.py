"""
BQS Oracle Sync Master - Self-Healing Synchronization
======================================================

This script fetches opportunities from Oracle CRM and syncs them to PostgreSQL
using UPSERT logic (INSERT ... ON CONFLICT DO UPDATE).

Features:
- ✅ Validates incoming data (no nulls for critical fields)
- ✅ Self-healing: Updates existing records, inserts new ones
- ✅ Marks stale records (optional)
- ✅ Handles errors gracefully
- ✅ Can run every 5 minutes without breaking

Usage:
    python scripts/sync_oracle_master.py           # Full sync
    python scripts/sync_oracle_master.py --clean   # Mark stale records
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import requests
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from typing import List, Dict, Optional

# Oracle CRM Configuration
ORACLE_CONFIG = {
    'base_url': os.getenv('ORACLE_BASE_URL', 'https://eijs-test.fa.em2.oraclecloud.com'),
    'username': os.getenv('ORACLE_USERNAME', 'yasasvi.upadrasta@inspiraenterprise.com'),
    'password': os.getenv('ORACLE_PASSWORD', 'Welcome@123'),
    'endpoint': '/crmRestApi/resources/latest/opportunities'
}

# PostgreSQL Configuration
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'bqs'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'Abcd1234'),
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': os.getenv('DB_PORT', '5432')
}

class OracleSyncMaster:
    """Self-healing Oracle to PostgreSQL synchronization"""
    
    def __init__(self):
        self.oracle_session = requests.Session()
        self.oracle_session.auth = (ORACLE_CONFIG['username'], ORACLE_CONFIG['password'])
        self.db_conn = None
        
    def connect_db(self):
        """Connect to PostgreSQL"""
        self.db_conn = psycopg2.connect(**DB_CONFIG)
        self.db_conn.autocommit = False
        
    def fetch_oracle_opportunities(self) -> List[Dict]:
        """Fetch all active opportunities from Oracle CRM"""
        print("\n📡 Fetching opportunities from Oracle CRM...")
        
        url = f"{ORACLE_CONFIG['base_url']}{ORACLE_CONFIG['endpoint']}"
        params = {
            # 'q': 'StatusCode=OPEN',  # Fetch ALL to ensure we catch everything
            'limit': 500,
            'fields': 'OptyId,OptyNumber,Name,Revenue,WinProb,SalesStage,OwnerName,PrimaryContactName,CloseDate,TargetPartyName,CurrencyCode,EffectiveDate,StatusCode'
        }
        
        try:
            response = self.oracle_session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            opportunities = data.get('items', [])
            
            print(f"✓ Fetched {len(opportunities)} opportunities from Oracle")
            return opportunities
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Oracle API Error: {e}")
            return []
    
    def validate_opportunity(self, opp: Dict) -> Optional[Dict]:
        """Validate and transform Oracle opportunity data"""
        
        # Required fields
        if not opp.get('OptyNumber'):
            print(f"⚠️  Skipping opportunity: Missing OptyNumber")
            return None
            
        if not opp.get('Name'):
            print(f"⚠️  Skipping {opp.get('OptyNumber')}: Missing Name")
            return None
        
        # Safe extraction for fields that might be missing or custom
        def get_val(keys, default=None):
            for k in keys:
                if opp.get(k): return opp[k]
            return default

        # Determine Workflow Status
        # If open in CRM -> NEW_FROM_CRM (unless already in a workflow state in DB - which upsert handles via "ON CONFLICT DO UPDATE" logic on fields, but we should be careful not to overwrite valid workflow states)
        # Actually, upsert overwrites everything unless we exclude it.
        # But here we generate the dict. 
        # The SQL below handles the "DO UPDATE SET".
        
        # Logic: 
        # - We return 'oracle_status' to be used in SQL logic.
        oracle_status = opp.get('StatusCode', 'OPEN')
        
        return {
            'remote_id': str(opp['OptyNumber']),
            'name': opp['Name'],
            'deal_value': float(opp.get('Revenue', 0) or 0),
            'win_probability': int(opp.get('WinProb', 0) or 0),
            'stage': opp.get('SalesStage', 'Unknown'),
            'sales_owner': opp.get('OwnerName'),
            'customer': opp.get('TargetPartyName') or opp.get('PrimaryContactName'), # Prefer Account Name
            'close_date': opp.get('CloseDate') or opp.get('EffectiveDate'),
            'currency': opp.get('CurrencyCode', 'USD'),
            'practice': get_val(['BusinessUnit', 'Practice_c', 'OptyPractice_c'], 'Unknown'),
            'geo': get_val(['Territory', 'Geo_c', 'OptyGeo_c'], 'Unknown'),
            'region': get_val(['Region_c', 'OptyRegion_c'], 'Unknown'),
            'sector': get_val(['Industry', 'Sector_c'], 'Unknown'),
            'oracle_status': oracle_status, # Pass this through
            'last_synced_at': datetime.now()
        }
    
    def upsert_opportunities(self, opportunities: List[Dict]):
        """
        UPSERT opportunities using PostgreSQL's ON CONFLICT DO UPDATE
        """
        print(f"\n💾 Upserting {len(opportunities)} opportunities...")
        
        if not opportunities:
            print("⚠️  No valid opportunities to sync")
            return
        
        cursor = self.db_conn.cursor()
        
        # The magic UPSERT query
        # We need conditional logic for workflow_status:
        # If EXCLUDED.oracle_status is NOT OPEN -> force CLOSED_IN_CRM
        # If EXCLUDED.oracle_status IS OPEN -> Keep existing status (do NOT overwrite if it's already in a workflow), OR set to NEW_FROM_CRM if it was CLOSED?
        # A simpler approach for the requested "Everything stored, only Open displayed":
        # If CRM status is closed -> workflow_status = 'CLOSED_IN_CRM'
        # If CRM status is open -> Do NOT change workflow_status (preserve user's workflow), UNLESS it was 'CLOSED_IN_CRM' previously?
        # Actually, 'NEW_FROM_CRM' is the default for INSERT.
        
        upsert_sql = """
        INSERT INTO opportunities (
            remote_id, name, deal_value, win_probability, stage,
            sales_owner, customer, close_date, currency,
            practice, geo, region, sector,
            last_synced_at, workflow_status
        ) VALUES %s
        ON CONFLICT (remote_id) 
        DO UPDATE SET
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
        
        # Prepare values
        values = []
        for opp in opportunities:
            # Determine initial status
            is_open = opp['oracle_status'].upper() == 'OPEN'
            initial_status = 'NEW_FROM_CRM' if is_open else 'CLOSED_IN_CRM'
            
            values.append((
                opp['remote_id'],
                opp['name'],
                opp['deal_value'],
                opp['win_probability'],
                opp['stage'],
                opp['sales_owner'],
                opp['customer'],
                opp['close_date'],
                opp['currency'],
                opp['practice'],
                opp['geo'],
                opp['region'],
                opp['sector'],
                opp['last_synced_at'],
                initial_status
            ))

        try:
            execute_values(cursor, upsert_sql, values)
            self.db_conn.commit()
            print(f"✓ Successfully upserted {len(opportunities)} opportunities")
            
        except Exception as e:
            self.db_conn.rollback()
            print(f"❌ Upsert failed: {e}")
            raise
        finally:
            cursor.close()
    
    def mark_stale_records(self, oracle_ids: List[str]):
        """Mark records as stale if they no longer exist in Oracle (e.g. Closed/Lost)"""
        print("\n🧹 Checking for stale records...")
        
        cursor = self.db_conn.cursor()
        
        # Find records in DB that are not in Oracle fetch (Open fetch)
        # We mark them as CLOSED_IN_CRM
        # We process batches to avoid massive NOT IN clauses if needed, but for <few thousand it's fine.
        
        if not oracle_ids:
             # If no oracle IDs returned, EVERYTHING might be stale? Or fetch failed?
             # Safe guard: if oracle_ids is empty, do nothing to avoid wiping DB on network error.
             print("⚠️  No Oracle IDs to compare. Skipping stale check.")
             cursor.close()
             return

        cursor.execute("""
            UPDATE opportunities 
            SET workflow_status = 'CLOSED_IN_CRM'
            WHERE remote_id NOT IN %s
            AND workflow_status != 'CLOSED_IN_CRM'
        """, (tuple(oracle_ids),))
        
        stale_count = cursor.rowcount
        self.db_conn.commit()
        
        if stale_count > 0:
            print(f"✓ Marked {stale_count} records as CLOSED_IN_CRM")
        else:
            print("✓ No new stale records found")
        
        cursor.close()
    
    def sync(self, mark_stale=False):
        """Main synchronization process"""
        print("\n" + "="*60)
        print("🔄 BQS ORACLE SYNC MASTER")
        print("="*60)
        
        try:
            # Step 1: Connect to database
            print("\n[1/4] Connecting to PostgreSQL...")
            self.connect_db()
            print("✓ Connected")
            
            # Step 2: Fetch from Oracle
            print("\n[2/4] Fetching from Oracle CRM...")
            oracle_opps = self.fetch_oracle_opportunities()
            
            if not oracle_opps:
                print("⚠️  No opportunities fetched from Oracle")
                return
            
            # Step 3: Validate and transform
            print("\n[3/4] Validating data...")
            valid_opps = []
            oracle_ids = []
            
            for opp in oracle_opps:
                validated = self.validate_opportunity(opp)
                if validated:
                    valid_opps.append(validated)
                    oracle_ids.append(validated['remote_id'])
            
            print(f"✓ {len(valid_opps)}/{len(oracle_opps)} opportunities validated")
            
            # Step 4: Upsert to database
            print("\n[4/4] Syncing to database...")
            self.upsert_opportunities(valid_opps)
            
            # Optional: Mark stale records
            if mark_stale and oracle_ids:
                self.mark_stale_records(oracle_ids)
            
            print("\n" + "="*60)
            print("✅ SYNC COMPLETE!")
            print("="*60)
            print(f"\nSummary:")
            print(f"  • Fetched: {len(oracle_opps)} opportunities")
            print(f"  • Valid: {len(valid_opps)} opportunities")
            print(f"  • Synced: {len(valid_opps)} opportunities")
            print("\n💡 Your database is now in sync with Oracle CRM")
            print("="*60)
            
        except Exception as e:
            print(f"\n❌ Sync failed: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            if self.db_conn:
                self.db_conn.close()

def main():
    """Entry point"""
    mark_stale = '--clean' in sys.argv
    
    syncer = OracleSyncMaster()
    syncer.sync(mark_stale=mark_stale)

if __name__ == "__main__":
    main()
