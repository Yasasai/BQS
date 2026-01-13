import time
import os
import sys
import psycopg2
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Add parent directory to path to find backend modules if needed
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# --- CONFIGURATION (Hardcoded for Robustness as requested) ---
ORACLE_USER = "yasasvi.upadrasta@inspiraenterprise.com"
ORACLE_PASS = "Welcome@123"
ORACLE_URL = "https://eijs-test.fa.em2.oraclecloud.com"
OPTY_LIST_URL = "https://eijs-test.fa.em2.oraclecloud.com/fscmUI/faces/FndOverview?fndGlobalItemNodeId=MOO_OPPTY"

# Database Config (Matches project .env)
DB_HOST = "127.0.0.1"
DB_NAME = "bqs"
DB_USER = "postgres"
DB_PASS = "Abcd1234"

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST
    )

def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Uncomment to run invisible
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=chrome_options)

def clean_amount(amount_str):
    """Converts '270,000 USD' to float 270000.0"""
    if not amount_str: return 0.0
    try:
        # Remove currency and commas
        clean = amount_str.split(' ')[0].replace(',', '')
        return float(clean)
    except:
        return 0.0

def scrape_oracle():
    print("🚀 Starting Oracle UI Scraper...")
    
    # 1. DB Check
    try:
        conn = get_db_connection()
        print("✅ Database connection established.")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return

    driver = setup_driver()
    wait = WebDriverWait(driver, 20)

    try:
        # 2. LOGIN
        print(f"🔑 Logging in to {ORACLE_URL}...")
        driver.get(ORACLE_URL)
        
        # Oracle Fusion Login Page Logic
        # Try to find standard UserID field
        try:
            user_field = wait.until(EC.presence_of_element_located((By.ID, "userid")))
            user_field.clear()
            user_field.send_keys(ORACLE_USER)
            
            pass_field = driver.find_element(By.ID, "password")
            pass_field.clear()
            pass_field.send_keys(ORACLE_PASS)
            
            sign_in_btn = driver.find_element(By.ID, "btnActive")
            sign_in_btn.click()
            print("   -> Credentials submitted.")
        except TimeoutException:
            print("   ⚠️  Login fields not found. Might already be logged in or SSO redirected.")
            time.sleep(5)

        # Wait for dashboard
        time.sleep(10)
        
        # 3. NAVIGATE TO OPPORTUNITIES
        print(f"🧭 Navigating to Opportunity List...")
        driver.get(OPTY_LIST_URL)
        time.sleep(8) # Allow heavy grid to load

        # 4. CRAWLER LOOP
        page_count = 0
        total_records = 0
        
        while True:
            page_count += 1
            print(f"\n📄 Scraping Page {page_count}...")
            
            # Re-locate rows to avoid StaleElementReference
            try:
                # Based on screenshot, it's a standard table. 
                # Generic strategy: Look for TRs that have data
                rows = wait.until(EC.presence_of_all_elements_located(
                    (By.XPATH, "//table[contains(@summary, 'Opportunit')]//tr")
                ))
            except TimeoutException:
                print("   ⚠️  Table not found. URL might be wrong or loading failed.")
                break

            print(f"   Found {len(rows)} potential rows.")
            
            batch_data = []
            
            for row in rows:
                try:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) < 12: continue # Header or empty row check based on screenshot columns

                    # MAPPING BASED ON SCREENSHOT
                    # [0] Win %, [1] OptyNum, [2] Name, [3] Owner, [4] Practice
                    # [5] Status, [6] CreateDate, [7] Account, [8] AcctOwner, 
                    # [9] Amount, [10] EstBill, [11] SalesStage, [12] Region
                    
                    opty_num = cols[1].text.strip()
                    if not opty_num or not opty_num.isdigit(): continue

                    name = cols[2].text.strip()
                    owner = cols[3].text.strip()
                    practice = cols[4].text.strip()
                    status = cols[5].text.strip()
                    account = cols[7].text.strip()
                    amount_raw = cols[9].text.strip()
                    stage = cols[11].text.strip()
                    region = cols[12].text.strip() if len(cols) > 12 else ""
                    
                    deal_val = clean_amount(amount_raw)
                    
                    batch_data.append((
                        opty_num, name, account, practice, region, 
                        deal_val, owner, stage, status
                    ))
                    
                except Exception:
                    continue
            
            # SAVE BATCH
            if batch_data:
                cursor = conn.cursor()
                # Upsert into 'opportunities' table
                # We map to the existing schema to keep backend compatible
                sql = """
                    INSERT INTO opportunities 
                    (remote_id, name, customer, practice, region, deal_value, sales_owner, stage, status, workflow_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'NEW')
                    ON CONFLICT (remote_id) 
                    DO UPDATE SET 
                        deal_value = EXCLUDED.deal_value,
                        stage = EXCLUDED.stage,
                        status = EXCLUDED.status,
                        sales_owner = EXCLUDED.sales_owner,
                        practice = EXCLUDED.practice;
                """
                cursor.executemany(sql, batch_data)
                conn.commit()
                total_records += len(batch_data)
                print(f"   ✅ Saved {len(batch_data)} records (Total: {total_records})")
            
            # PAGINATION
            try:
                # Look for 'Next' button (Title usually 'Next Set' or 'Next' in Oracle Fusion)
                # Icons often have title attributes
                next_btn = driver.find_element(By.XPATH, "//a[@title='Next'] | //img[@title='Next'] | //button[text()='Next']")
                
                # Check if disabled (Oracle usually grays it out or removes href)
                if "Disabled" in next_btn.get_attribute("class") or "disabled" in next_btn.get_attribute("src") :
                    print("🛑 Next button disabled. End of list.")
                    break
                    
                next_btn.click()
                print("   ➡️ Clicking Next...")
                time.sleep(5) # Wait for Ajax reload
                
            except NoSuchElementException:
                print("🛑 No 'Next' button found (Single page result).")
                break
                
    except Exception as e:
        print(f"❌ Critical Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'driver' in locals(): driver.quit()
        if 'conn' in locals(): conn.close()
        print(f"🎉 Crawler Finished. Total Synced: {total_records}")

if __name__ == "__main__":
    scrape_oracle()
