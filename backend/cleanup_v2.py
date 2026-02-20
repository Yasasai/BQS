import os

path = r"C:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS\backend\app\routers\opportunities.py"
try:
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Line 401: {lines[400]}")
    print(f"Line 453: {lines[452]}")

    if "=======" not in lines[400]:
        print("Marker 401 not found")
        # Search for it
        for i, line in enumerate(lines):
            if "=======" in line:
                print(f"Found ======= at index {i}")
                start_idx = i
                break
        else:
            print("======= not found at all")
            exit(1)
    else:
        start_idx = 400

    if ">>>>>>>" not in lines[452]:
        print("Marker 453 not found")
        for i in range(start_idx, len(lines)):
            if ">>>>>>>" in line: # BUG: lines[i]
                print(f"Found >>>>>>> at index {i}")
                end_idx = i
                break
            if ">>>>>>>" in lines[i]:
                 end_idx = i
                 break
        else:
             print(">>>>>>> not found")
             exit(1)
    else:
        end_idx = 452

    # We want to remove start_idx to end_idx inclusive
    new_lines = lines[:start_idx] + lines[end_idx+1:]
    
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Success")

except Exception as e:
    print(e)
