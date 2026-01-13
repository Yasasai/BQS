import os
from dotenv import load_dotenv

load_dotenv('.env')
user = os.getenv("ORACLE_USER")
pwd = os.getenv("ORACLE_PASSWORD")

with open('final_status.txt', 'w') as f:
    f.write(f"USER={user}\n")
    f.write(f"PASS={pwd}\n")
    if not user or not pwd:
        f.write("FALLBACK_TRIGGERED\n")
        try:
            with open('.env', 'r', encoding='utf-8') as ef:
                for line in ef:
                    if '=' in line:
                        k, v = line.split('=', 1)
                        if k.strip() == "ORACLE_USER": f.write(f"MANUAL_USER={v.strip()}\n")
                        if k.strip() == "ORACLE_PASSWORD": f.write(f"MANUAL_PASS={v.strip()}\n")
        except Exception as e:
            f.write(f"ERROR={e}\n")
