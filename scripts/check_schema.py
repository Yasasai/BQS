
import psycopg2

def check():
    try:
        conn = psycopg2.connect(dbname='bqs', user='postgres', password='Abcd1234', host='127.0.0.1', port=5432)
        cur = conn.cursor()
        
        cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'opp_score_version';")
        print("Columns in opp_score_version:")
        for col in cur.fetchall():
            print(f"  {col[0]}: {col[1]}")
            
        cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'opp_score_section_value';")
        print("\nColumns in opp_score_section_value:")
        for col in cur.fetchall():
            print(f"  {col[0]}: {col[1]}")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check()
