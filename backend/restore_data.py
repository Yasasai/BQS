import os
import json
import psycopg2
from datetime import datetime

# Connection details
DB_CONFIG = {
    "dbname": "bqs",
    "user": "postgres",
    "password": "Abcd1234",
    "host": "127.0.0.1",
    "port": 5432
}

def restore_all_data():
    dump_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database_dump.json')
    if not os.path.exists(dump_path):
        print(f"❌ No backup found at {dump_path}")
        return

    try:
        with open(dump_path, 'r') as f:
            master_data = json.load(f)

        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Disable triggers/constraints temporarily if needed, or restore in order
        print("\n[1/3] Restoring Users...")
        for user in master_data.get("users", []):
            cur.execute("""
                INSERT INTO users (id, email, name, role) 
                VALUES (%s, %s, %s, %s) 
                ON CONFLICT (id) DO UPDATE SET 
                email = EXCLUDED.email, name = EXCLUDED.name, role = EXCLUDED.role
            """, (user['id'], user['email'], user['name'], user['role']))

        print("[2/3] Restoring Opportunities...")
        opps = master_data.get("opportunities", [])
        for opp in opps:
            # Dynamically build columns and values to avoid hardcoded mismatch
            columns = opp.keys()
            placeholders = ", ".join(["%s"] * len(columns))
            cols_str = ", ".join(columns)
            update_str = ", ".join([f"{col} = EXCLUDED.{col}" for col in columns if col != 'id'])
            
            cur.execute(f"""
                INSERT INTO opportunities ({cols_str}) 
                VALUES ({placeholders}) 
                ON CONFLICT (id) DO UPDATE SET {update_str}
            """, list(opp.values()))

        print("[3/3] Restoring Assessments...")
        for ass in master_data.get("assessments", []):
            # Convert JSON back to proper format if needed
            scores = json.dumps(ass['scores']) if isinstance(ass['scores'], (dict, list)) else ass['scores']
            risks = json.dumps(ass['risks']) if isinstance(ass['risks'], (dict, list)) else ass['risks']
            
            cur.execute("""
                INSERT INTO assessments (id, opp_id, version, scores, comments, risks, is_submitted, created_at, created_by) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                opp_id = EXCLUDED.opp_id, version = EXCLUDED.version, scores = EXCLUDED.scores, 
                comments = EXCLUDED.comments, risks = EXCLUDED.risks, is_submitted = EXCLUDED.is_submitted,
                created_at = EXCLUDED.created_at, created_by = EXCLUDED.created_by
            """, (ass['id'], ass['opp_id'], ass['version'], scores, ass['comments'], risks, ass['is_submitted'], ass['created_at'], ass['created_by']))

        conn.commit()
        print(f"\n✅ SUCCESS: All data restored from {dump_path}")
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error restoring data: {e}")

if __name__ == "__main__":
    restore_all_data()
