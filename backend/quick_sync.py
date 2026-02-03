"""
Quick sync script using SQLAlchemy (no psycopg2 needed)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs"

try:
    print("🔄 Connecting to database...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("✅ Connected! Running sync query...")
        
        # Execute the update
        result = conn.execute(text("""
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
            WHERE o.opp_id = v.opp_id
        """))
        
        conn.commit()
        print(f"✅ Updated {result.rowcount} opportunities!")
        
        # Show summary
        summary = conn.execute(text("""
            SELECT workflow_status, COUNT(*) as count
            FROM opportunity 
            WHERE workflow_status IS NOT NULL
            GROUP BY workflow_status
            ORDER BY count DESC
        """))
        
        print("\n📊 Current workflow_status distribution:")
        for row in summary:
            print(f"   {row[0]}: {row[1]} opportunities")
            
    print("\n✅ Sync completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
