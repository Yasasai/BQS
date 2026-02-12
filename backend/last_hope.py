import os

path = r"C:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS\backend\app\routers\opportunities.py"

try:
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    line404 = lines[403] # 0-indexed
    line429 = lines[428] # 0-indexed
    
    print(f"Line 404: {line404.rstrip()}")
    print(f"Line 429: {line429.rstrip()}")
    
    if "elif role == 'SH'" not in line404:
        print("Warning: Line 404 mismatch")
        
    if ">>>>>>>" not in line429:
        print("Warning: Line 429 mismatch")

    # Delete 404-430 inclusive (indices 403-429)
    # Keep :403 (0..402)
    # Keep 430: (430..end)
    new_lines = lines[:403] + lines[430:]
    
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Success")
except Exception as e:
    print(e)
