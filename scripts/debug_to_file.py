
import psycopg2
import json

def debug():
    try:
        conn = psycopg2.connect(dbname='bqs', user='postgres', password='Abcd1234', host='127.0.0.1', port=5432)
        cur = conn.cursor()
        
        target_opp = "300003780261059"
        
        results = {}
        
        # 1. Opportunity Table
        cur.execute("SELECT * FROM opportunity WHERE opp_id = %s", (target_opp,))
        row = cur.fetchone()
        if row:
            colnames = [d[0] for d in cur.description]
            results['opportunity'] = dict(zip(colnames, [str(v) if v is not None else None for v in row]))
        
        # 2. Score Version
        cur.execute("SELECT * FROM opp_score_version WHERE opp_id = %s ORDER BY version_no DESC", (target_opp,))
        versions = cur.fetchall()
        results['versions'] = []
        if versions:
            colnames = [d[0] for d in cur.description]
            for v in versions:
                results['versions'].append(dict(zip(colnames, [str(item) if item is not None else None for item in v])))
        
        # 3. Overall stats
        cur.execute("SELECT status, count(*) FROM opp_score_version GROUP BY status")
        results['stats'] = dict(cur.fetchall())
        
        with open('debug_output.json', 'w') as f:
            json.dump(results, f, indent=2)
            
        print("Debug data written to debug_output.json")
        
    except Exception as e:
        with open('debug_output.json', 'w') as f:
            f.write(f"Error: {str(e)}")

if __name__ == "__main__":
    debug()
