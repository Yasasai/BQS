
import psycopg2

def migrate():
    try:
        conn = psycopg2.connect(
            dbname='bqs',
            user='postgres',
            password='Abcd1234',
            host='127.0.0.1',
            port=5432
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        print("Checking/Updating schema...")
        
        # 1. Update OppScoreVersion
        cur.execute("ALTER TABLE opp_score_version ADD COLUMN IF NOT EXISTS attachment_name VARCHAR;")
        print("✓ opp_score_version.attachment_name ensured")
        
        # 2. Update OppScoreSectionValue
        cur.execute("ALTER TABLE opp_score_section_value ADD COLUMN IF NOT EXISTS selected_reasons JSONB;")
        print("✓ opp_score_section_value.selected_reasons ensured")
        
        # 3. Handle score column type change (Integer -> Float)
        # We use DOUBLE PRECISION for Float in Postgres
        cur.execute("ALTER TABLE opp_score_section_value ALTER COLUMN score TYPE DOUBLE PRECISION;")
        print("✓ opp_score_section_value.score type updated to Float")
        
        cur.close()
        conn.close()
        print("\n✅ Migration complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    migrate()
