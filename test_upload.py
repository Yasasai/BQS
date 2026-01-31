
import requests
import os

BASE_URL = "http://localhost:8000/api"

def test_flow():
    # 1. Test Upload
    print("--- 1. Testing Upload ---")
    try:
        test_file_path = "test_upload.txt"
        with open(test_file_path, "w") as f:
            f.write("This is a test attachment.")
            
        with open(test_file_path, "rb") as f:
            files = {"file": f}
            res = requests.post(f"{BASE_URL}/upload", files=files)
            
        if res.status_code == 200:
            print(f"✅ Upload Success: {res.json()}")
        else:
            print(f"❌ Upload Failed: {res.status_code} - {res.text}")
            
        os.remove(test_file_path)
    except Exception as e:
        print(f"⚠️ Upload Test Error (Is server running?): {e}")

if __name__ == "__main__":
    test_flow()
