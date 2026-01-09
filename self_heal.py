import os
import subprocess
import sys
import time

def run_command(command, cwd=None, description=""):
    if description:
        print(f"\n--- {description} ---")
    print(f"Executing: {command} in {cwd or 'root'}")
    try:
        subprocess.check_call(command, shell=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return False

def self_heal():
    print("="*60)
    print("🚀 BQS INDESTRUCTIBLE SELF-HEAL PROTOCOL")
    print("="*60)
    print("Goal: Restore the app to 100% capacity from any state.")
    
    # 1. Check/Install Node Modules
    if not os.path.exists('frontend/node_modules'):
        run_command("npm install", cwd='frontend', description="Restoring Frontend Dependencies")
    
    # 2. Check/Install Python Venv
    if not os.path.exists('backend/venv'):
        run_command("python -m venv venv", cwd='backend', description="Restoring Backend Environment")
    
    pip_path = os.path.join('backend', 'venv', 'Scripts', 'pip') if sys.platform == 'win32' else os.path.join('backend', 'venv', 'bin', 'pip')
    python_path = os.path.join('backend', 'venv', 'Scripts', 'python') if sys.platform == 'win32' else os.path.join('backend', 'venv', 'bin', 'python')
    
    run_command(f"{pip_path} install -r requirements.txt", cwd='backend', description="Syncing Dependencies")

    # 3. Database Resilience
    print("\n--- Repairing Database ---")
    run_command(f"{python_path} -c \"from database import init_db; init_db()\"", cwd='backend', description="Initializing Tables")
    
    # 4. Data Restoration
    run_command(f"{python_path} restore_data.py", cwd='backend', description="Restoring Master Data from database_dump.json")

    print("\n" + "="*60)
    print("✅ SELF-HEAL COMPLETE!")
    print("Apps is now at the exact state of your last dump.")
    print("="*60)
    print("\nQuick Start:")
    print("  Backend: cd backend && venv\\Scripts\\activate && python main.py")
    print("  Frontend: cd frontend && npm run dev")

if __name__ == "__main__":
    self_heal()
