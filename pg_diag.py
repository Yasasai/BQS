import psycopg2
import json

def diagnostic():
    db_url = "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs"
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        print("--- TARGET OPPORTUNITIES ---")
        cur.execute("""
            SELECT opp_id, opp_name, workflow_status, is_active, 
                   assigned_practice_head_id, assigned_sales_head_id,
                   gh_approval_status, ph_approval_status, sh_approval_status
            FROM opportunities 
            WHERE opp_name ILIKE '%RetailCo%' OR opp_name ILIKE '%Acme%'
        """)
        rows = cur.fetchall()
        for r in rows:
            print(r)
            
        print("\n--- PH USERS ---")
        cur.execute("SELECT user_id, display_name, role FROM users WHERE role = 'PH'")
        print(cur.fetchall())
        
        print("\n--- SH USERS ---")
        cur.execute("SELECT user_id, display_name, role FROM users WHERE role = 'SH'")
        print(cur.fetchall())
        
        conn.close()
    except Exception as e:
        print(f"PostgreSQL Diagnostic Error: {e}")

if __name__ == "__main__":
    diagnostic()
