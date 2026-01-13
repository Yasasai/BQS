
import os
import re
import sys
from PIL import Image

try:
    import pytesseract
except ImportError:
    print("❌ pytesseract not installed")
    sys.exit(1)

# Common Tesseract paths
tesseract_paths = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Users\\' + os.getlogin() + r'\AppData\Local\Tesseract-OCR\tesseract.exe'
]
for path in tesseract_paths:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        break

def extract_from_file(file_path):
    if not os.path.exists(file_path):
        print(f"❌ File {file_path} not found")
        return
    
    print(f"🔍 Reading {file_path}...")
    img = Image.open(file_path).convert('L')
    text = pytesseract.image_to_string(img)
    
    opportunity_ids = re.findall(r"\b\d{6,7}\b", text)
    opportunity_ids = list(dict.fromkeys(opportunity_ids))
    
    print("\n" + "="*30)
    print(f"🎯 IDS FROM {file_path}:")
    print("="*30)
    for opty_id in opportunity_ids:
        print(f"  - {opty_id}")
    print("="*30)

if __name__ == "__main__":
    # Check for the user's specific image or the screenshot
    if os.path.exists("opportunities.jpg"):
        extract_from_file("opportunities.jpg")
    if os.path.exists("full_screenshot.png"):
        extract_from_file("full_screenshot.png")
