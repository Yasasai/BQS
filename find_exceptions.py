import os
import re

logs = []
for root, dirs, files in os.walk('backend'):
    for f in files:
        if f.endswith('.log') or f.endswith('.txt'):
            logs.append(os.path.join(root, f))

pattern = re.compile(r'.{0,100}(InFailedSqlTransaction|IntegrityError|DataError|NotNullViolation|psycopg2\.errors|sqlalchemy\.exc).{0,200}', re.IGNORECASE)

matches = []
for log_file in logs:
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if pattern.search(line):
                    matches.append(f"{log_file}:{i+1}: {line.strip()}")
    except Exception as e:
        pass

with open('exception_search.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(matches))

print(f"Found {len(matches)} matches. Written to exception_search.txt")
