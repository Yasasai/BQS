import os

path = r"C:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS\backend\app\routers\opportunities.py"
out_path = r"C:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS\backend\app\routers\opportunities_fixed.py"

try:
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Determine range to cut
    start_cut = -1
    end_cut = -1
    
    for i, line in enumerate(lines):
        # Look for the start of duplicate SH block around line 404
        if i > 400 and "elif role == 'SH' and user_id:" in line:
            start_cut = i
            break
            
    for i, line in enumerate(lines):
        # Look for end marker around line 429
        if i > 400 and ">>>>>>>" in line:
            end_cut = i
            break
            
    if start_cut == -1 or end_cut == -1:
        print(f"Could not find cut points: {start_cut}, {end_cut}")
        # Print nearby lines for debug
        print("\nContext around 404:")
        for j in range(400, min(410, len(lines))):
            print(f"{j}: {lines[j].rstrip()}")
        print("\nContext around 429:")
        for j in range(max(0, 420), min(440, len(lines))):
            print(f"{j}: {lines[j].rstrip()}")
        exit(1)
        
    print(f"Cutting lines {start_cut} to {end_cut} (inclusive of marker, maybe +1 for brace)")
    
    # Check brace at end_cut + 1
    if end_cut + 1 < len(lines) and "}" in lines[end_cut+1]:
        end_cut += 1 # improved cut to include brace
        
    new_lines = lines[:start_cut] + lines[end_cut+1:]
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
        
    print(f"Wrote {len(new_lines)} lines to {out_path}")
    
except Exception as e:
    print(e)
