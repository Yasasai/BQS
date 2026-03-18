import psycopg2

def seed():
    conn = psycopg2.connect("postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs")
    conn.autocommit = False
    cur = conn.cursor()
    
    try:
        # Get SH and SA users
        cur.execute("SELECT u.user_id FROM app_user u JOIN user_role ur ON u.user_id = ur.user_id JOIN role r ON ur.role_id = r.role_id WHERE r.role_code = 'SH' LIMIT 1;")
        sh_res = cur.fetchone()
        sh_id = sh_res[0] if sh_res else None
        
        cur.execute("SELECT u.user_id FROM app_user u JOIN user_role ur ON u.user_id = ur.user_id JOIN role r ON ur.role_id = r.role_id WHERE r.role_code = 'SA' LIMIT 1;")
        sa_res = cur.fetchone()
        sa_id = sa_res[0] if sa_res else None

        if not sh_id or not sa_id:
            print(f"Missing SH ({sh_id}) or SA ({sa_id}). Exiting.")
            return
            
        print(f"Assigning SH: {sh_id}")
        print(f"Assigning SA: {sa_id}")

        cur.execute("SELECT opp_id FROM opportunity ORDER BY opp_id LIMIT 20;")
        opps = cur.fetchall()
        
        for i, (opp_id,) in enumerate(opps):
            # Update all 20: set sales_owner_user_id and assigned_sales_head_id to the SH's UUID.
            cur.execute("UPDATE opportunity SET sales_owner_user_id = %s, assigned_sales_head_id = %s WHERE opp_id = %s", (sh_id, sh_id, opp_id))
            
            # Update 5 of those 20: set assigned_sa_id to the SA's UUID and update the workflow_status to 'ASSIGNED_TO_SA'.
            if i < 5:
                cur.execute("UPDATE opportunity SET assigned_sa_id = %s, workflow_status = 'ASSIGNED_TO_SA' WHERE opp_id = %s", (sa_id, opp_id))
                
        conn.commit()
        print(f"Successfully updated {len(opps)} opportunities.")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    seed()
