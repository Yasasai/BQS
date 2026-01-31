
"""
BQS Universal Setup Script
===========================

This script sets up the entire BQS project from scratch.
Perfect for:
- New developers joining the project
- Recovering after a crash
- Fresh clone from GitHub

What it does:
1. ✅ Checks Python and Node.js are installed
2. ✅ Creates Python virtual environment
3. ✅ Installs backend dependencies (requirements.txt)
4. ✅ Installs frontend dependencies (npm install)
5. ✅ Checks PostgreSQL connection
6. ✅ Creates database if needed
7. ✅ Runs schema migrations
8. ✅ Optionally syncs data from Oracle

Usage:
    python scripts/setup/setup_project.py
    python scripts/setup/setup_project.py --with-data  # Also populate test data
"""

import subprocess
import sys
import os
from pathlib import Path

# Fix path to root
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(ROOT_DIR)

class Colors:
    """Terminal colors"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_step(step, message):
    """Print formatted step"""
    print(f"\n{Colors.BOLD}[{step}]{Colors.END} {message}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✓{Colors.END} {message}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}❌{Colors.END} {message}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️ {Colors.END} {message}")

def run_command(cmd, cwd=None, check=True):
    """Run shell command"""
    try:
        # If running python, ensure we use the venv python if available
        # But if we are creating venv, we use system python.
        result = subprocess.run(
            cmd,
            cwd=cwd,
            shell=True,
            capture_output=True,
            text=True,
            check=check
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_python():
    """Check Python version"""
    print_step("1/8", "Checking Python...")
    success, stdout, _ = run_command("python --version", check=False)
    
    if success:
        version = stdout.strip()
        print_success(f"Python found: {version}")
        return True
    else:
        print_error("Python not found! Please install Python 3.8+")
        return False

def check_node():
    """Check Node.js version"""
    print_step("2/8", "Checking Node.js...")
    success, stdout, _ = run_command("node --version", check=False)
    
    if success:
        version = stdout.strip()
        print_success(f"Node.js found: {version}")
        return True
    else:
        print_warning("Node.js not found. Frontend won't work without it.")
        return False

def setup_backend_venv():
    """Create Python virtual environment"""
    print_step("3/8", "Setting up Python virtual environment...")
    
    venv_path = os.path.join(ROOT_DIR, "backend", "venv")
    
    if os.path.exists(venv_path):
        print_success("Virtual environment already exists")
        return True
    
    # Use explicit path creation
    success, _, stderr = run_command(f"python -m venv {os.path.join('backend', 'venv')}", cwd=ROOT_DIR)
    
    if success:
        print_success("Virtual environment created")
        return True
    else:
        print_error(f"Failed to create venv: {stderr}")
        return False

def install_backend_deps():
    """Install Python dependencies"""
    print_step("4/8", "Installing backend dependencies...")
    
    pip_cmd = os.path.join("backend", "venv", "Scripts", "pip") if os.name == 'nt' else "backend/venv/bin/pip"
    python_cmd = os.path.join("backend", "venv", "Scripts", "python") if os.name == 'nt' else "backend/venv/bin/python"
    req_path = os.path.join("backend", "requirements.txt")
    
    # First upgrade pip to avoid permission issues
    print("  Upgrading pip...")
    run_command(f"{python_cmd} -m pip install --upgrade pip", cwd=ROOT_DIR, check=False)
    
    # Install dependencies
    print("  Installing packages...")
    success, stdout, stderr = run_command(f"{pip_cmd} install -r {req_path}", cwd=ROOT_DIR, check=False)
    
    if success or "Successfully installed" in stdout:
        print_success("Backend dependencies installed")
        return True
    else:
        print_error(f"Failed to install dependencies: {stderr}")
        print(f"Output: {stdout}")
        return False

def install_frontend_deps():
    """Install Node.js dependencies"""
    print_step("5/8", "Installing frontend dependencies...")
    
    frontend_path = os.path.join(ROOT_DIR, "frontend")
    if not os.path.exists(os.path.join(frontend_path, "package.json")):
        print_warning("No package.json found, skipping")
        return True
    
    success, _, stderr = run_command("npm install", cwd=frontend_path)
    
    if success:
        print_success("Frontend dependencies installed")
        return True
    else:
        print_error(f"Failed to install npm packages: {stderr}")
        return False

def check_postgres():
    """Check PostgreSQL connection"""
    print_step("6/8", "Checking PostgreSQL...")
    
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='Abcd1234',
            host='127.0.0.1',
            port=5432
        )
        conn.close()
        print_success("PostgreSQL connection successful")
        return True
    except ImportError:
         print_warning("psycopg2 not installed in system python, assuming venv has it. Skipping system check.")
         return True
    except Exception as e:
        print_error(f"PostgreSQL connection failed: {e}")
        print_warning("Make sure PostgreSQL is running on localhost:5432")
        print_warning("Default credentials: postgres / Abcd1234")
        return False

def create_database_and_migrate():
    """Create BQS database and tables"""
    print_step("7/8", "Setting up database and tables...")
    
    try:
        # We invoke the init_db directly from the backend code
        # We need to ensure we run this using the VENV python!
        
        python_cmd = os.path.join("backend", "venv", "Scripts", "python") if os.name == 'nt' else "backend/venv/bin/python"
        
        # We create a temporary script runner to execute init_db
        runner_code = """
import sys
import os
sys.path.append(os.getcwd())
from backend.app.core.database import init_db
init_db()
"""
        runner_path = os.path.join(ROOT_DIR, "init_runner.py")
        with open(runner_path, "w") as f:
            f.write(runner_code)
            
        success, stdout, stderr = run_command(f"{python_cmd} init_runner.py", cwd=ROOT_DIR)
        
        if os.path.exists(runner_path):
            os.remove(runner_path)
            
        if success:
            print_success("Database initialized and seeded.")
            return True
        else:
            print_error(f"Database initialization failed: {stderr}")
            print(stdout)
            return False
            
    except Exception as e:
        print_error(f"Database setup failed: {e}")
        return False

def populate_data():
    """Populate with Oracle Sync"""
    print_step("8/8", "Populating test data (Sync)...")
    
    python_cmd = os.path.join("backend", "venv", "Scripts", "python") if os.name == 'nt' else "backend/venv/bin/python"
    
    # Run sync manager
    script_path = os.path.join("backend", "app", "services", "sync_manager.py")
    success, stdout, stderr = run_command(f"{python_cmd} {script_path}", cwd=ROOT_DIR)
    
    if success:
        print_success("Data synchronization complete")
        print(stdout)
        return True
    else:
        print_error(f"Sync failed: {stderr}")
        return False

def main():
    """Main setup process"""
    print("\n" + "="*70)
    print(f"{Colors.BOLD}🚀 BQS PROJECT SETUP (RESTRUCTURED){Colors.END}")
    print("="*70)
    print("\nThis will set up everything you need to run BQS.\n")
    
    with_data = '--with-data' in sys.argv
    
    # Run all setup steps
    steps = [
        ("Python", check_python),
        ("Node.js", check_node),
        ("Virtual Environment", setup_backend_venv),
        ("Backend Dependencies", install_backend_deps),
        ("Frontend Dependencies", install_frontend_deps),
        ("PostgreSQL", check_postgres),
        ("Database & Schema", create_database_and_migrate),
    ]
    
    if with_data:
        steps.append(("Oracle Sync", populate_data))
    
    failed = []
    
    for name, func in steps:
        if not func():
            failed.append(name)
    
    # Summary
    print("\n" + "="*70)
    if not failed:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ SETUP COMPLETE!{Colors.END}")
        print("="*70)
        print("\n🎯 Next Steps:\n")
        print("  1. Start Backend:")
        print("     cd backend")
        print("     venv\\Scripts\\python -m backend.app.main")
        print("\n  2. Start Frontend (new terminal):")
        print("     cd frontend")
        print("     npm run dev")
        
        if not with_data:
            print("\n💡 To populate real data:")
            print("     python scripts/setup/setup_project.py --with-data")
        
        print("\n" + "="*70)
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ SETUP INCOMPLETE{Colors.END}")
        print("="*70)
        print(f"\nFailed steps: {', '.join(failed)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
