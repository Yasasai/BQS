
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def execute_sql():
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        print(f"Connecting to {DATABASE_URL}")
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
        sql = """
-- Insert the Legal Lead Role (if it doesn't already exist)
INSERT INTO role (role_id, role_code, role_name) 
VALUES (99, 'LL', 'Legal Lead')
ON CONFLICT (role_code) DO NOTHING;

-- Insert the Dummy User
INSERT INTO app_user (user_id, email, display_name, is_active, created_at)
VALUES ('dummy-legal-001', 'legal.lead@example.com', 'Dummy Legal Lead', true, NOW())
ON CONFLICT (email) DO NOTHING;

-- Map the User to the Role
INSERT INTO user_role (user_id, role_id)
SELECT 'dummy-legal-001', role_id FROM role WHERE role_code = 'LL'
ON CONFLICT (user_id, role_id) DO NOTHING;
        """
        
        cur.execute(sql)
        print("SQL executed successfully.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error executing SQL: {e}")

if __name__ == "__main__":
    execute_sql()
