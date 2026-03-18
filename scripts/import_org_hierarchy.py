import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback/Default for local development if .env is missing or doesn't have it
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/bqs"

engine = create_engine(DATABASE_URL)

CSV_DIR = r"c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS"

ROLE_MAPPING = {
    "Bid Manager": "BM",
    "Finance": "FL",
    "Legal": "LL",
    "Practice Head": "PH",
    "Sales Head": "SH",
    "Sales Person": "SP"
}

def get_role_id(conn, role_code):
    result = conn.execute(text("SELECT role_id FROM role WHERE role_code = :code"), {"code": role_code}).fetchone()
    if result:
        return result[0]
    return None

def upsert_user(conn, email, display_name, manager_email=None, corporate_title=None, geo_region=None, practice_name=None):
    # Check if user exists
    user = conn.execute(text("SELECT user_id FROM app_user WHERE email = :email"), {"email": email}).fetchone()
    if user:
        user_id = user[0]
        conn.execute(text("""
            UPDATE app_user 
            SET display_name = :display_name, 
                manager_email = :manager_email, 
                corporate_title = :corporate_title, 
                geo_region = :geo_region, 
                practice_name = :practice_name,
                is_active = true
            WHERE user_id = :user_id
        """), {
            "display_name": display_name,
            "manager_email": manager_email,
            "corporate_title": corporate_title,
            "geo_region": geo_region,
            "practice_name": practice_name,
            "user_id": user_id
        })
    else:
        import uuid
        user_id = str(uuid.uuid4())
        conn.execute(text("""
            INSERT INTO app_user (user_id, email, display_name, manager_email, corporate_title, geo_region, practice_name, is_active)
            VALUES (:user_id, :email, :display_name, :manager_email, :corporate_title, :geo_region, :practice_name, true)
        """), {
            "user_id": user_id,
            "email": email,
            "display_name": display_name,
            "manager_email": manager_email,
            "corporate_title": corporate_title,
            "geo_region": geo_region,
            "practice_name": practice_name
        })
    return user_id

def assign_role(conn, user_id, role_id):
    if not role_id:
        return
    # Check if assignment exists
    exists = conn.execute(text("SELECT 1 FROM user_role WHERE user_id = :u_id AND role_id = :r_id"), 
                         {"u_id": user_id, "r_id": role_id}).fetchone()
    if not exists:
        conn.execute(text("INSERT INTO user_role (user_id, role_id) VALUES (:u_id, :r_id)"), 
                     {"u_id": user_id, "r_id": role_id})

def process_csvs():
    with engine.begin() as conn:
        # Get role IDs
        roles = {code: get_role_id(conn, code) for code in ROLE_MAPPING.values()}
        
        # 1. Bid Manager.csv
        bm_path = os.path.join(CSV_DIR, "Bid Manager.csv")
        if os.path.exists(bm_path):
            print("Processing Bid Manager.csv...")
            df = pd.read_csv(bm_path)
            for _, row in df.iterrows():
                email = row['Email']
                if pd.isna(email) or not str(email).strip(): continue
                uid = upsert_user(conn, email.strip(), row['Bid Manager'], geo_region=row['Geo'])
                assign_role(conn, uid, roles['BM'])

        # 2. Finance.csv
        fin_path = os.path.join(CSV_DIR, "Finance.csv")
        if os.path.exists(fin_path):
            print("Processing Finance.csv...")
            df = pd.read_csv(fin_path)
            for _, row in df.iterrows():
                email = row['Email']
                if pd.isna(email) or not str(email).strip(): continue
                uid = upsert_user(conn, email.strip(), row['Name'], corporate_title=row['Role'])
                assign_role(conn, uid, roles['FL'])

        # 3. Legal.csv
        leg_path = os.path.join(CSV_DIR, "Legal.csv")
        if os.path.exists(leg_path):
            print("Processing Legal.csv...")
            df = pd.read_csv(leg_path)
            for _, row in df.iterrows():
                email = row['Email']
                if pd.isna(email) or not str(email).strip(): continue
                uid = upsert_user(conn, email.strip(), row['Name'], corporate_title=row['Role'])
                assign_role(conn, uid, roles['LL'])

        # 4. Practice.csv
        prac_path = os.path.join(CSV_DIR, "Practice.csv")
        if os.path.exists(prac_path):
            print("Processing Practice.csv...")
            df = pd.read_csv(prac_path)
            for _, row in df.iterrows():
                email = row['Emails'] # Note the 's' in Emails
                if pd.isna(email) or not str(email).strip(): continue
                uid = upsert_user(conn, email.strip(), row['Practice Head'], practice_name=row['Practice Name'])
                assign_role(conn, uid, roles['PH'])

        # 5. Sales hierarchy.csv
        sales_path = os.path.join(CSV_DIR, "Sales hierarchy.csv")
        if os.path.exists(sales_path):
            print("Processing Sales hierarchy.csv...")
            df = pd.read_csv(sales_path)
            # Assuming columns: Name, Email, Role, Manager Email, etc. based on common hierarchy patterns
            # Let's try to detect columns or use likely ones.
            # From previous grep, we know 'Email' exists.
            
            # If 'Sales Head' logic is needed, we map accordingly.
            for _, row in df.iterrows():
                email = row.get('Email') or row.get('email')
                if pd.isna(email) or not str(email).strip(): continue
                
                name = row.get('Name') or row.get('Employee Name') or "Unknown"
                manager = row.get('Manager Email') or row.get('Reporting Manager Email')
                title = row.get('Designation') or row.get('Role')
                geo = row.get('Region') or row.get('Geo')
                
                uid = upsert_user(conn, email.strip(), name, manager_email=manager, corporate_title=title, geo_region=geo)
                
                # Role detection for Sales
                role_code = 'SP' # Default to Sales Person
                if title and ('Head' in str(title) or 'VP' in str(title) or 'Director' in str(title)):
                    role_code = 'SH'
                
                assign_role(conn, uid, roles[role_code])

if __name__ == "__main__":
    process_csvs()
    print("Ingestion complete.")
