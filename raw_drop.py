
import psycopg2

try:
    conn = psycopg2.connect(
        dbname='bqs', 
        user='postgres', 
        password='Abcd1234', 
        host='127.0.0.1', 
        port=5432
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        tables = [
            "opp_score_section_values", 
            "opp_score_section_value", 
            "opp_score_version", 
            "opportunity_assignment", 
            "user_role", 
            "app_user", 
            "role", 
            "sync_run", 
            "opp_score_section"
        ]
        for t in tables:
            print(f"Dropping {t}...")
            cur.execute(f"DROP TABLE IF EXISTS {t} CASCADE;")
        print("✅ Tables dropped via raw SQL.")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
