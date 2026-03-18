
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in the environment")
engine = create_engine(DATABASE_URL)

def deduplicate():
    with engine.connect() as conn:
        print("Finding duplicates in opp_score_version...")
        # Subquery to identify which version IDs to delete
        delete_ids_sql = """
            SELECT score_version_id
            FROM (
                SELECT score_version_id,
                       ROW_NUMBER() OVER (PARTITION BY opp_id, version_no ORDER BY created_at DESC) as row_num
                FROM opp_score_version
            ) t
            WHERE t.row_num > 1
        """
        
        # 1. Delete dependent values first
        print("Deleting dependent section values...")
        conn.execute(text(f"DELETE FROM opp_score_values WHERE score_version_id IN ({delete_ids_sql})"))
        
        # 2. Delete the version rows
        print("Deleting duplicate version rows...")
        result = conn.execute(text(f"DELETE FROM opp_score_version WHERE score_version_id IN ({delete_ids_sql})"))
        
        conn.commit()
        print(f"Deleted {result.rowcount} duplicate versions and their dependent values.")

if __name__ == "__main__":
    deduplicate()
