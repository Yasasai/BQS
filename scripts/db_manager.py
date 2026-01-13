"""
BQS Database Management Script
===============================
Consolidated script for all database operations:
- Self-healing migrations
- Data population
- Database verification

Usage:
    python scripts/db_manager.py heal      # Fix schema issues
    python scripts/db_manager.py populate  # Add test data
    python scripts/db_manager.py check     # Verify database
    python scripts/db_manager.py reset     # Heal + Populate
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import psycopg2
from datetime import datetime

DB_CONFIG = {
    'dbname': 'bqs',
    'user': 'postgres',
    'password': 'Abcd1234',
    'host': '127.0.0.1',
    'port': 5432
}

def get_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def heal_database():
    """Add missing columns to opportunities table"""
    print("\n🔧 Self-Healing Database Schema...")
    
    columns_to_add = [
        ('workflow_status', 'VARCHAR'),
        ('assigned_sa', 'VARCHAR'),
        ('assigned_practice', 'VARCHAR'),
        ('sa_notes', 'TEXT'),
        ('practice_head_recommendation', 'VARCHAR'),
        ('practice_head_notes', 'TEXT'),
        ('management_decision', 'VARCHAR'),
        ('close_reason', 'TEXT'),
        ('sa_owner', 'VARCHAR'),
        ('status', 'VARCHAR DEFAULT \'New from CRM\''),
    ]
    
    conn = get_connection()
    conn.autocommit = True
    cursor = conn.cursor()
    
    added = 0
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='opportunities' AND column_name='{col_name}'
                    ) THEN
                        ALTER TABLE opportunities ADD COLUMN {col_name} {col_type};
                        RAISE NOTICE 'Added: {col_name}';
                    END IF;
                END $$;
            """)
            added += 1
        except Exception as e:
            print(f"  ⚠️  {col_name}: {e}")
    
    cursor.close()
    conn.close()
    print(f"✓ Schema check complete ({added} columns verified)")

def populate_test_data():
    """Populate database with test data"""
    print("\n📝 Populating Test Data...")
    
    conn = get_connection()
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Clear existing
    cursor.execute("DELETE FROM opportunities")
    
    # Test data
    test_data = [
        ("OPP-1001", "Enterprise Cloud Platform", "Global Tech Inc", "Cloud", 
         1500000, "USD", 75, "Sarah Johnson", "3. Qualify", "NEW_FROM_CRM",
         None, None, None, None, None),
        ("OPP-1002", "Security Assessment", "FinTech Solutions", "Cybersecurity",
         850000, "USD", 80, "Mike Chen", "2. Develop", "ASSIGNED_TO_PRACTICE",
         None, "Cybersecurity", None, None, None),
        ("OPP-1003", "Data Analytics Platform", "Retail Corp", "Analytics",
         650000, "USD", 70, "Lisa Wang", "3. Qualify", "ASSIGNED_TO_SA",
         "Jane Smith", "Analytics", "Analyzing requirements", None, None),
        ("OPP-1004", "Deal Z - Cloud Migration", "Enterprise Corp", "Cloud",
         2200000, "USD", 85, "John Martinez", "4. Commit", "WAITING_PH_APPROVAL",
         "David Wilson", "Cloud", "Strong technical fit", None, None),
        ("OPP-1005", "ERP Implementation", "Manufacturing Ltd", "ERP",
         1800000, "USD", 78, "Amanda Lee", "3. Qualify", "WAITING_PH_APPROVAL",
         "Michael Chen", "ERP", "Good opportunity", None, None),
        ("OPP-1006", "Cybersecurity Transformation", "Banking Solutions", "Cybersecurity",
         3500000, "USD", 90, "Robert Kim", "4. Commit", "READY_FOR_MGMT_REVIEW",
         "Jane Smith", "Cybersecurity", "Excellent fit", "APPROVED", "Strong recommendation"),
        ("OPP-1007", "Digital Transformation", "Healthcare Systems", "Digital",
         2800000, "USD", 88, "Emily Brown", "4. Commit", "READY_FOR_MGMT_REVIEW",
         "David Wilson", "Digital", "Well-aligned", "APPROVED", "Approved"),
    ]
    
    sql = """
    INSERT INTO opportunities (
        remote_id, name, customer, practice, deal_value, currency,
        win_probability, sales_owner, stage, workflow_status,
        assigned_sa, assigned_practice, sa_notes,
        practice_head_recommendation, practice_head_notes, last_synced_at
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
    """
    
    for data in test_data:
        cursor.execute(sql, data)
    
    print(f"✓ Inserted {len(test_data)} opportunities")
    
    # Show summary
    cursor.execute("SELECT workflow_status, COUNT(*) FROM opportunities GROUP BY workflow_status ORDER BY workflow_status")
    print("\n📊 Summary:")
    for status, count in cursor.fetchall():
        marker = "⭐" if status in ["WAITING_PH_APPROVAL", "READY_FOR_MGMT_REVIEW"] else ""
        print(f"  • {status}: {count} {marker}")
    
    cursor.close()
    conn.close()

def check_database():
    """Check database status"""
    print("\n📊 Database Status Check...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM opportunities")
    total = cursor.fetchone()[0]
    print(f"✓ Total opportunities: {total}")
    
    if total > 0:
        cursor.execute("SELECT workflow_status, COUNT(*) FROM opportunities GROUP BY workflow_status")
        print("\nBreakdown:")
        for status, count in cursor.fetchall():
            print(f"  • {status}: {count}")
    
    cursor.close()
    conn.close()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        if command == 'heal':
            heal_database()
        elif command == 'populate':
            populate_test_data()
        elif command == 'check':
            check_database()
        elif command == 'reset':
            heal_database()
            populate_test_data()
            print("\n✅ Database reset complete!")
        else:
            print(f"Unknown command: {command}")
            print(__doc__)
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
