
import psycopg2
from datetime import datetime

def find_submitted_assessments():
    try:
        conn = psycopg2.connect(
            dbname='bqs',
            user='postgres',
            password='Abcd1234',
            host='127.0.0.1',
            port=5432
        )
        cursor = conn.cursor()
        
        # Check OppScoreVersion table
        print("Checking opp_score_version table for SUBMITTED records...")
        cursor.execute("SELECT opp_id, version_no, status, created_at, created_by_user_id FROM opp_score_version WHERE status = 'SUBMITTED'")
        rows = cursor.fetchall()
        
        if not rows:
            print("No SUBMITTED records found in opp_score_version.")
        else:
            print(f"Found {len(rows)} submitted records:")
            for r in rows:
                print(f"  Opp ID: {r[0]}, Version: {r[1]}, Status: {r[2]}, Created: {r[3]}, By User: {r[4]}")

        # Check Opportunity table for calculated statuses if any columns exist
        print("\nChecking opportunity table...")
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'opportunity'")
        cols = [c[0] for c in cursor.fetchall()]
        print(f"Columns in opportunity: {cols}")
        
        if 'workflow_status' in cols:
            cursor.execute("SELECT opp_id, opp_name, workflow_status FROM opportunity WHERE workflow_status = 'SUBMITTED_FOR_REVIEW'")
            rows = cursor.fetchall()
            print(f"Opportunities with workflow_status='SUBMITTED_FOR_REVIEW': {len(rows)}")
            for r in rows:
                print(f"  ID: {r[0]}, Name: {r[1]}, Status: {r[2]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_submitted_assessments()
