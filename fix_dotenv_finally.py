import os
import sys

# Standard BQS Keys
REQUIRED_KEYS = ["ORACLE_USER", "ORACLE_PASSWORD"]

def fix():
    print("--- 🛠️ FINAL DOTENV FIXER 🛠️ ---")
    
    current_dir = os.getcwd()
    env_path = os.path.join(current_dir, '.env')
    
    print(f"Path: {env_path}")
    
    # 1. READ CONTENT
    content = ""
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"Existing file found ({len(content)} chars)")
    else:
        print("❌ .env NOT FOUND!")
        
    # 2. FORCE REWRITE WITH CLEAN CONTENT
    # Using your actual credentials from previous successful runs
    new_content = [
        "ORACLE_USER=yasasvi.upadrasta@inspiraenterprise.com",
        "ORACLE_PASS=Welcome@123",
        "ORACLE_PASSWORD=Welcome@123",
        "ORACLE_BASE_URL=https://eijs-test.fa.em2.oraclecloud.com",
        "ORACLE_URL=https://eijs-test.fa.em2.oraclecloud.com",
        "ORACLE_TOKEN_URL=",
        "ORACLE_CLIENT_ID=",
        "ORACLE_CLIENT_SECRET=",
        "ORACLE_SCOPE=https://eijs-test.fa.em2.oraclecloud.com:443/crmRestApi/resources/latest/"
    ]
    
    # Clean write (LF line endings, no BOM)
    with open(env_path, 'w', newline='\n', encoding='utf-8') as f:
        f.write("\n".join(new_content) + "\n")
    
    print("✓ Forced rewrite completed.")
    
    # 3. VERIFY LOAD
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_path, override=True)
    
    for key in REQUIRED_KEYS:
        val = os.getenv(key)
        print(f"   [{key}]: {'✅ LOADED' if val else '❌ MISSING'}")
        if val:
            print(f"      Value preview: {val[:4]}...{val[-4:]}")

    if all(os.getenv(k) for k in REQUIRED_KEYS):
        print("\n🎉 EVERYTHING READY!")
    else:
        print("\n🛑 STILL MISSING KEYS!")

if __name__ == "__main__":
    fix()
