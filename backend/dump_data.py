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

def datetime_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

def dump_table(cur, table_name):
    print(f"Dumping table: {table_name}...")
    cur.execute(f"SELECT * FROM {table_name}")
    colnames = [desc[0] for desc in cur.description]
    results = cur.fetchall()
    return [dict(zip(colnames, row)) for row in results]

def dump_all_data():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        master_data = {
            "opportunities": dump_table(cur, "opportunities"),
            "assessments": dump_table(cur, "assessments"),
            "users": dump_table(cur, "users")
        }
            
        dump_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database_dump.json')
        with open(dump_path, 'w') as f:
            json.dump(master_data, f, default=datetime_handler, indent=4)
            
        print(f"\n✅ SUCCESS: All data dumped to {dump_path}")
        print(f"   - Opportunities: {len(master_data['opportunities'])}")
        print(f"   - Assessments: {len(master_data['assessments'])}")
        print(f"   - Users: {len(master_data['users'])}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error dumping data: {e}")

if __name__ == "__main__":
    dump_all_data()
