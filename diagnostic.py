import os
import sys
from dotenv import load_dotenv

print(f"Current Working Directory: {os.getcwd()}")
base_path = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_path, '.env')

print(f"Target .env path: {env_path}")
print(f"File exists: {os.path.exists(env_path)}")

if os.path.exists(env_path):
    print(f"File size: {os.path.getsize(env_path)} bytes")
    try:
        loaded = load_dotenv(dotenv_path=env_path)
        print(f"load_dotenv(dotenv_path='{env_path}') returned: {loaded}")
        
        user = os.getenv("ORACLE_USER")
        pwd = os.getenv("ORACLE_PASSWORD")
        
        print(f"ORACLE_USER found: {'***' + user[-4:] if user else 'None'}")
        print(f"ORACLE_PASSWORD found: {'***' + pwd[-4:] if pwd else 'None'}")
        
        # Check all env vars loaded by dotenv
        print("Variables in .env (keys only):")
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key = line.split('=')[0].strip()
                    print(f"  - {key}")
                    
    except Exception as e:
        print(f"Error reading/loading .env: {e}")
else:
    print("Project directory contains:")
    print(os.listdir(base_path))
