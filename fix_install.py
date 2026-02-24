"""
Quick Fix Script - Install Dependencies Manually
"""
import subprocess
import sys
import os

def run_cmd(cmd):
    """Run command and show output"""
    print(f"\n▶ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr and "Successfully installed" not in result.stderr:
        print(result.stderr)
    return result.returncode == 0

print("="*60)
print("BQS Quick Fix - Installing Dependencies")
print("="*60)

# Determine venv paths
if os.name == 'nt':
    python_exe = r"backend\venv\Scripts\python.exe"
    pip_exe = r"backend\venv\Scripts\pip.exe"
else:
    python_exe = "backend/venv/bin/python"
    pip_exe = "backend/venv/bin/pip"

print("\n[1/3] Upgrading pip...")
run_cmd(f"{python_exe} -m pip install --upgrade pip")

print("\n[2/3] Installing all dependencies...")
run_cmd(f"{pip_exe} install -r backend/requirements.txt")

print("\n[3/3] Verifying installation...")
success = run_cmd(f'{python_exe} -c "import psycopg2; import fastapi; import httpx; print(\\"✓ All critical packages installed!\\")"')

print("\n" + "="*60)
if success:
    print("✅ Installation Complete!")
    print("="*60)
    print("\nNext step: Run the setup script:")
    print("  python scripts/setup/setup_project.py --with-data")
else:
    print("❌ Some packages failed to install")
    print("="*60)
    print("\nTry running manually:")
    print(f"  {pip_exe} install psycopg2-binary fastapi httpx")

print()
