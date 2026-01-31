"""
Quick database check - verify opportunities exist
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs"

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Count all opportunities
        result = conn.execute(text("SELECT COUNT(*) FROM opportunity WHERE is_active = true"))
        count = result.scalar()
        print(f"📊 Total active opportunities in database: {count}")
        
        if count > 0:
            # Show first 5
            result = conn.execute(text("""
                SELECT opp_id, opp_name, workflow_status 
                FROM opportunity 
                WHERE is_active = true 
                LIMIT 5
            """))
            
            print("\n🔍 Sample opportunities:")
            for row in result:
                status = row[2] or 'NULL'
                print(f"   - {row[0]}: {row[1]} (Status: {status})")
        else:
            print("\n⚠️ No opportunities found in database!")
            print("   Run: python insert_test_opportunities.py")
            
except Exception as e:
    print(f"❌ Error: {e}")
