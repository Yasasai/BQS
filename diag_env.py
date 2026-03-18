import sys
import os
print(f"EXE: {sys.executable}")
print(f"CWD: {os.getcwd()}")
print(f"PATH: {sys.path}")
print("Listing site-packages:")
sp_path = os.path.join("backend", "venv", "Lib", "site-packages")
if os.path.exists(sp_path):
    for d in os.listdir(sp_path):
        if "jose" in d.lower():
            print(f" - {d}")
else:
    print(f"SP path not found: {sp_path}")

try:
    import jose
    print("SUCCESS: jose imported")
except ImportError as e:
    print(f"FAIL: {e}")
except Exception as e:
    print(f"ERROR: {e}")
