
try:
    from PIL import Image
    import pytesseract
except ImportError:
    print("❌ Critical: Please run 'pip install Pillow pytesseract' first.")
    sys.exit(1)

import re
import os
import sys
import csv
from datetime import datetime

# Add project root and backend to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ['PYTHONPATH'] = os.path.join(BASE_DIR, 'backend')
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'backend'))

print(f"📂 Project Root: {BASE_DIR}")

try:
    from backend.database import SessionLocal, Opportunity, OpportunityDetails, init_db
except ImportError:
    try:
        from database import SessionLocal, Opportunity, OpportunityDetails, init_db
    except ImportError as e:
        print(f"❌ ImportError: {e}")
        print(f"Current Path: {sys.path}")
        sys.exit(1)

def extract_and_seed(image_path="opportunities.jpg"):
    print(f"👁️  Processing screenshot: {image_path}...")
    
    if not os.path.exists(image_path):
        print(f"❌ Error: Could not find {image_path}. Please ensure the image is in the project root.")
        return

    try:
        # Using PIL instead of OpenCV to avoid numpy dependency issues
        img = Image.open(image_path)
        # Convert to grayscale for better OCR visibility
        img = img.convert('L') 
        
        text = pytesseract.image_to_string(img)
        
        rows = []
        print("🔍 Parsing OCR data...")
        for line in text.split("\n"):
            # Match Win% (100) and Opp No (6-7 digits)
            if re.search(r"\b100\b", line) and re.search(r"\d{6,7}", line):
                win = "100"
                opp_no_match = re.search(r"\b\d{6,7}\b", line)
                if opp_no_match:
                    opp_no = opp_no_match.group(0)
                    parts = line.split(opp_no)
                    name = parts[1].strip() if len(parts) > 1 else "Unknown"
                    name = re.sub(r'[^a-zA-Z0-9\s\-_]', '', name)
                    rows.append({"win": win, "id": opp_no, "name": name})

        if not rows:
            print("❌ No opportunities found via OCR. Ensure Tesseract is installed and path is set.")
            return

        print(f"✅ Extracted {len(rows)} records. Seeding database...")
        
        # Save a backup CSV using built-in module
        with open("extracted_opportunities.csv", "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["win", "id", "name"])
            writer.writeheader()
            writer.writerows(rows)

        init_db()
        db = SessionLocal()
        try:
            for row in rows:
                existing = db.query(Opportunity).filter(Opportunity.remote_id == row['id']).first()
                opp_data = {
                    "remote_id": row['id'],
                    "name": row['name'],
                    "win_probability": float(row['win']),
                    "workflow_status": "NEW_FROM_CRM",
                    "last_synced_at": datetime.utcnow()
                }
                if existing:
                    for key, val in opp_data.items(): setattr(existing, key, val)
                else:
                    db.add(Opportunity(**opp_data))
                
                # Seed Details
                if not db.query(OpportunityDetails).filter(OpportunityDetails.opty_number == row['id']).first():
                    db.add(OpportunityDetails(
                        opty_number=row['id'], 
                        name=row['name'], 
                        win_probability=float(row['win']),
                        raw_json={"source": "OCR_SCREENSHOT"}
                    ))
            db.commit()
            print(f"🚀 Success! {len(rows)} opportunities added.")
        except Exception as e:
            print(f"❌ DB Error: {e}")
            db.rollback()
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ OCR Process Error: {e}")

if __name__ == "__main__":
    extract_and_seed()
