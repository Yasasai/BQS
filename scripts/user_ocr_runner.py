
import os
import re
import sys
import time

# Robust dependency loading for Python 3.14
try:
    from PIL import Image, ImageGrab
except ImportError:
    print("❌ Critical: 'Pillow' is missing. Run: pip install Pillow")
    sys.exit(1)

try:
    import pytesseract
except ImportError:
    print("❌ Critical: 'pytesseract' is missing. Run: pip install pytesseract")
    sys.exit(1)

# Configure Tesseract path (Common windows locations)
tesseract_paths = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Users\\' + os.getlogin() + r'\AppData\Local\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
]

tesseract_found = False
for path in tesseract_paths:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        tesseract_found = True
        break

if not tesseract_found:
    print("❌ Error: Tesseract-OCR not found. Please install it or update the path in the script.")
    sys.exit(1)

def run_user_extraction():
    screenshot_path = "user_request_screenshot.png"
    
    print("📸 Capturing current screen...")
    try:
        # Using ImageGrab (Pillow) as a more robust alternative to pyautogui for 3.14
        screenshot = ImageGrab.grab()
        screenshot.save(screenshot_path)
        print(f"✅ Saved screenshot to {screenshot_path}")
    except Exception as e:
        print(f"❌ Failed to capture screen: {e}")
        # Fallback to existing if available
        if os.path.exists("opportunities.jpg"):
            screenshot_path = "opportunities.jpg"
            print(f"🔄 Falling back to existing file: {screenshot_path}")
        else:
            return

    print("🔍 Performing OCR Analysis...")
    try:
        img = Image.open(screenshot_path).convert('L') # Grayscale for better OCR
        text = pytesseract.image_to_string(img)
        
        # Regex for 6-7 digit opportunity IDs
        opportunity_ids = re.findall(r"\b\d{6,7}\b", text)
        
        # Unique and Sorted
        opportunity_ids = sorted(list(dict.fromkeys(opportunity_ids)))
        
        print("\n" + "="*40)
        print("🎯 EXTRACTED OPPORTUNITY IDS:")
        print("="*40)
        if opportunity_ids:
            for opty_id in opportunity_ids:
                print(f"  ID: {opty_id}")
            print(f"\nTotal Found: {len(opportunity_ids)}")
        else:
            print("  No IDs found in the current view.")
            print("  Make sure the CRM table is visible on the screen.")
        print("="*40)
        
    except Exception as e:
        print(f"❌ OCR Analysis failed: {e}")

if __name__ == "__main__":
    run_user_extraction()
