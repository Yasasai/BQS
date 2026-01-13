import os

# Content with your actual credentials
ENV_DATA = {
    "ORACLE_USER": "yasasvi.upadrasta@inspiraenterprise.com",
    "ORACLE_PASSWORD": "Welcome@123",
    "ORACLE_BASE_URL": "https://eijs-test.fa.em2.oraclecloud.com",
    "ORACLE_URL": "https://eijs-test.fa.em2.oraclecloud.com",
    "ORACLE_TOKEN_URL": "",
    "ORACLE_CLIENT_ID": "",
    "ORACLE_CLIENT_SECRET": "",
    "ORACLE_SCOPE": "https://eijs-test.fa.em2.oraclecloud.com:443/crmRestApi/resources/latest/"
}

def force_standard_env():
    env_path = os.path.join(os.getcwd(), '.env')
    
    # Write with strict UTF-8 (no BOM) and LF line endings
    with open(env_path, 'w', encoding='utf-8', newline='\n') as f:
        for key, value in ENV_DATA.items():
            f.write(f"{key}={value}\n")
    
    print(f"✅ Forced UTF-8 rewrite of {env_path}")
    print(f"   Size: {os.path.getsize(env_path)} bytes")

if __name__ == "__main__":
    force_standard_env()
