import os
import sys
import psycopg2
from psycopg2 import sql

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.core.database import DATABASE_URL

def add_columns():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()

    columns = [
        ("assigned_practice_head_id", "VARCHAR"),
        ("assigned_sales_head_id", "VARCHAR"),
        ("assigned_sa_id", "VARCHAR"),
        ("assigned_sp_id", "VARCHAR"),
        ("gh_approval_status", "VARCHAR DEFAULT 'PENDING'"),
        ("ph_approval_status", "VARCHAR DEFAULT 'PENDING'"),
        ("sh_approval_status", "VARCHAR DEFAULT 'PENDING'"),
        ("combined_submission_ready", "BOOLEAN DEFAULT FALSE")
    ]

    print("🚀 Adding workflow columns to 'opportunity' table...")

    for col_name, col_type in columns:
        try:
            cur.execute(sql.SQL("ALTER TABLE opportunity ADD COLUMN {} {}").format(
                sql.Identifier(col_name),
                sql.SQL(col_type)
            ))
            print(f"✅ Added column: {col_name}")
        except psycopg2.errors.DuplicateColumn:
            print(f"⚠️  Column already exists: {col_name}")
        except Exception as e:
            print(f"❌ Error adding {col_name}: {e}")

    conn.close()
    print("✨ Schema update complete.")

if __name__ == "__main__":
    add_columns()
