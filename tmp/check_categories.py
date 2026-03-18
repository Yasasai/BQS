
import psycopg2
import uuid

DB = dict(dbname="bqs", user="postgres", password="Abcd1234",
          host="127.0.0.1", port=5432)

CATEGORIES = [
    ('RFP', 'rfp'),
    ('Proposal', 'proposal'),
    ('RLS', 'rls'),
    ('Pricing', 'pricing'),
    ('Proxy Evidence', 'proxy')
]

def check_and_seed():
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM document_category")
        count = cur.fetchone()[0]
        print(f"Current document categories: {count}")
        
        if count == 0:
            print("Seeding document categories...")
            for label, cid in CATEGORIES:
                id_val = str(uuid.uuid4())
                cur.execute(
                    "INSERT INTO document_category (category_id, label_name, is_active) VALUES (%s, %s, %s)",
                    (id_val, label, True)
                )
            conn.commit()
            print("Seeding complete.")
        else:
            print("Categories already exist.")
            cur.execute("SELECT label_name FROM document_category")
            rows = cur.fetchall()
            for r in rows:
                print(f" - {r[0]}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_and_seed()
