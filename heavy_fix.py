import psycopg2

def heavy_fix():
    # Use the same URL as the app
    db_url = "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs"
    print(f"Connecting to {db_url}...")
    try:
        conn = psycopg2.connect(db_url, connect_timeout=10)
        conn.autocommit = True
        cur = conn.cursor()
        
        # 1. Ensure 'ph-001' and 'sh-001' users exist
        print("Checking users...")
        users_to_ensure = [
            ('ph-001', 'sarah.mitchell@company.com', 'Sarah Mitchell'),
            ('sh-001', 'robert.chen@company.com', 'Robert Chen'),
            ('gh-001', 'james.wilson@company.com', 'James Wilson')
        ]
        for uid, email, name in users_to_ensure:
            cur.execute("SELECT 1 FROM app_user WHERE user_id = %s", (uid,))
            if not cur.fetchone():
                print(f"Creating user {uid}...")
                cur.execute("INSERT INTO app_user (user_id, email, display_name, is_active, created_at) VALUES (%s, %s, %s, true, now())", (uid, email, name))
            else:
                print(f"User {uid} already exists.")

        # 2. Fix RetailCo and Acme
        print("Fixing target opportunities...")
        cur.execute("""
            UPDATE opportunity 
            SET workflow_status = 'READY_FOR_REVIEW',
                is_active = true,
                assigned_practice_head_id = 'ph-001',
                assigned_sales_head_id = 'sh-001',
                gh_approval_status = 'PENDING',
                ph_approval_status = 'PENDING',
                sh_approval_status = 'PENDING',
                local_last_synced_at = now()
            WHERE opp_name ILIKE '%RetailCo%' OR opp_name ILIKE '%Acme%'
        """)
        print(f"Updated {cur.rowcount} target opportunities.")

        # 3. Check for any NULL approval statuses and fix them for ALL active opps
        cur.execute("""
            UPDATE opportunity 
            SET gh_approval_status = 'PENDING' 
            WHERE gh_approval_status IS NULL AND is_active = true
        """)
        cur.execute("""
            UPDATE opportunity 
            SET ph_approval_status = 'PENDING' 
            WHERE ph_approval_status IS NULL AND is_active = true
        """)
        cur.execute("""
            UPDATE opportunity 
            SET sh_approval_status = 'PENDING' 
            WHERE sh_approval_status IS NULL AND is_active = true
        """)
        
        # 4. Final verification
        cur.execute("SELECT opp_name, workflow_status, assigned_practice_head_id FROM opportunity WHERE opp_name ILIKE '%RetailCo%'")
        print("Final Reality Check:", cur.fetchall())
        
        conn.close()
        print("✅ DATABASE FIX COMPLETE.")
    except Exception as e:
        print(f"❌ DATABASE FIX FAILED: {e}")

if __name__ == "__main__":
    heavy_fix()
