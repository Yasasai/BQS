import os

file_path = r'C:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS\backend\app\routers\opportunities.py'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Lines to remove: 402 to 454 (1-based)
    # Indices to remove: 401 to 453 (0-based)
    
    # Validation
    if not lines[401].strip().startswith("======="):
        print(f"Error: Line 402 content mismatch: {lines[401]}")
        exit(1)
        
    if not lines[453].strip().startswith(">>>>>>>"):
        print(f"Error: Line 454 content mismatch: {lines[453]}")
        exit(1)

    new_lines = lines[:401] + lines[454:]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
        
    print("Successfully removed conflict block.")
    
except Exception as e:
    print(f"Error: {e}")
