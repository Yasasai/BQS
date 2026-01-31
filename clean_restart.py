"""
Force Clean Restart - Clear Python Cache and Restart Backend
============================================================

This script clears all Python cache files and restarts the backend
to ensure the latest code changes are loaded.
"""

import os
import sys
import shutil
import subprocess

print("="*70)
print("🧹 CLEANING PYTHON CACHE")
print("="*70)

# Get project root
project_root = os.path.dirname(os.path.abspath(__file__))

# Remove __pycache__ directories
cache_count = 0
for root, dirs, files in os.walk(project_root):
    if '__pycache__' in dirs:
        cache_dir = os.path.join(root, '__pycache__')
        print(f"🗑️  Removing: {cache_dir}")
        shutil.rmtree(cache_dir)
        cache_count += 1

# Remove .pyc files
pyc_count = 0
for root, dirs, files in os.walk(project_root):
    for file in files:
        if file.endswith('.pyc'):
            pyc_file = os.path.join(root, file)
            print(f"🗑️  Removing: {pyc_file}")
            os.remove(pyc_file)
            pyc_count += 1

print(f"\n✅ Cleaned {cache_count} __pycache__ directories")
print(f"✅ Cleaned {pyc_count} .pyc files")

print("\n" + "="*70)
print("🚀 STARTING BACKEND WITH FRESH CODE")
print("="*70)

# Start backend
os.chdir(project_root)
subprocess.run([sys.executable, "-m", "backend.app.main"])
