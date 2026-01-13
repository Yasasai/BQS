
import os
import re
import sys

# Try to import dependencies with helpful error messages
try:
    from PIL import Image, ImageGrab
except ImportError:
    print("❌ Error: 'Pillow' not installed. Please run: pip install Pillow")
    sys.exit(1)

try:
    import pytesseract
except ImportError:
    print("❌ Error: 'pytesseract' not installed. Please run: pip install pytesseract")
    sys.exit(1)

# Helper to find tesseract on Windows
tesseract_paths = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Users\\' + os.getlogin() + r'\AppData\Local\Tesseract-OCR\tesseract.exe'
]

for path in tesseract_paths:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        break

def capture_and_extract():
    print("📸 Capturing screenshot...")
    try:
        # Capture the whole screen
        screenshot = ImageGrab.grab()
        screenshot.save("full_screenshot.png")
        print("✅ Screenshot saved to 'full_screenshot.png'")
        
        # Pre-process for OCR (Grayscale)
        gray_img = screenshot.convert('L')
        
        print("🔍 Performing OCR (this may take a few seconds)...")
        text = pytesseract.image_to_string(gray_img)
        
        # Extract 6-7 digit IDs
        opportunity_ids = re.findall(r"\b\d{6,7}\b", text)
        
        # Remove duplicates while preserving order
        opportunity_ids = list(dict.fromkeys(opportunity_ids))
        
        print("\n" + "="*30)
        print("🎯 EXTRACTED OPPORTUNITY IDS:")
        print("="*30)
        if opportunity_ids:
            for opty_id in opportunity_ids:
                print(f"  - {opty_id}")
        else:
            print("  No 6-7 digit IDs found.")
        print("="*30)
        
        return opportunity_ids

    except Exception as e:
        print(f"❌ Critical Failure: {e}")
        print("\nNote: On Windows, ensure Tesseract-OCR is installed.")
        return []

if __name__ == "__main__":
    capture_and_extract()
