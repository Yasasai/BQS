"""
Data Migration Script: Sync workflow_status from opp_score_version to opportunity table
This script updates the opportunity.workflow_status based on the latest assessment version status.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def sync_workflow_status():
    try:
        conn = psycopg2.connect(
            dbname='bqs', 
            user='postgres', 
            host='127.0.0.1', 
            password='Abcd1234', 
            port=5432,
            connect_timeout=5
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cur:
            print("🔄 Syncing workflow_status from opp_score_version to opportunity...")
            
            # Update workflow_status based on latest version status
            sync_query = """
            UPDATE opportunity o
            SET workflow_status = CASE
                WHEN v.status = 'SUBMITTED' THEN 'SUBMITTED_FOR_REVIEW'
                WHEN v.status = 'DRAFT' THEN 'UNDER_ASSESSMENT'
                WHEN v.status = 'APPROVED' THEN 'APPROVED'
                WHEN v.status = 'REJECTED' THEN 'REJECTED'
                WHEN v.status = 'ACCEPTED' THEN 'ACCEPTED'
                ELSE v.status
            END
            FROM (
                SELECT DISTINCT ON (opp_id) 
                    opp_id, 
                    status
                FROM opp_score_version
                ORDER BY opp_id, version_no DESC
            ) v
            WHERE o.opp_id = v.opp_id;
            """
            
            cur.execute(sync_query)
            rows_updated = cur.rowcount
            
            print(f"✅ Successfully updated {rows_updated} opportunities with workflow_status")
            
            # Show summary
            cur.execute("""
                SELECT workflow_status, COUNT(*) 
                FROM opportunity 
                WHERE workflow_status IS NOT NULL
                GROUP BY workflow_status
                ORDER BY COUNT(*) DESC;
            """)
            
            print("\n📊 Current workflow_status distribution:")
            for row in cur.fetchall():
                print(f"   {row[0]}: {row[1]} opportunities")
                
        conn.close()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")

if __name__ == "__main__":
    sync_workflow_status()
