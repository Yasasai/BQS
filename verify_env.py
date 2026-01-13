import os

# Absolute content based on previous successful credentials
env_content = """ORACLE_USER=yasasvi.upadrasta@inspiraenterprise.com
ORACLE_PASS=Welcome@123
ORACLE_PASSWORD=Welcome@123
ORACLE_BASE_URL=https://eijs-test.fa.em2.oraclecloud.com
ORACLE_URL=https://eijs-test.fa.em2.oraclecloud.com
ORACLE_TOKEN_URL=
ORACLE_CLIENT_ID=
ORACLE_CLIENT_SECRET=
ORACLE_SCOPE=https://eijs-test.fa.em2.oraclecloud.com:443/crmRestApi/resources/latest/
"""

with open('.env', 'w') as f:
    f.write(env_content)

print(f"Created .env file with {len(env_content)} characters.")

from dotenv import load_dotenv
load_dotenv()

user = os.getenv("ORACLE_USER")
pwd = os.getenv("ORACLE_PASSWORD")

print(f"Verification: USER={'FOUND' if user else 'NOT FOUND'}, PWD={'FOUND' if pwd else 'NOT FOUND'}")
if user:
    print(f"User ends with: {user[-4:]}")
