import sqlite3
import pandas as pd

def check_data():
    conn = sqlite3.connect('backend/bqs.db')
    
    # Check Opportunity Data
    print("--- Opportunity Data (RetailCo & Acme) ---")
    query = """
    SELECT 
        opp_name, 
        workflow_status, 
        assigned_practice_head_id, 
        assigned_sales_head_id, 
        assigned_sa_id,
        assigned_sp_id,
        gh_approval_status, 
        ph_approval_status, 
        sh_approval_status 
    FROM opportunities 
    WHERE opp_name LIKE '%RetailCo%' OR opp_name LIKE '%Acme%'
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string())
    
    print("\n--- User Data (PH, SH, GH) ---")
    user_query = "SELECT user_id, display_name, role, email FROM users WHERE role IN ('PH', 'SH', 'GH')"
    try:
        df_users = pd.read_sql_query(user_query, conn)
        print(df_users.to_string())
    except Exception as e:
        print(f"Could not read users: {e}")

    conn.close()

if __name__ == "__main__":
    check_data()
