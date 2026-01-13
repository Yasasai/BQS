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
    python scripts/setup_project.py
    python scripts/setup_project.py --with-data  # Also populate test data
"""

import subprocess
import sys
import os
from pathlib import Path

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
    
    venv_path = Path("backend/venv")
    
    if venv_path.exists():
        print_success("Virtual environment already exists")
        return True
    
    success, _, stderr = run_command("python -m venv backend/venv")
    
    if success:
        print_success("Virtual environment created")
        return True
    else:
        print_error(f"Failed to create venv: {stderr}")
        return False

def install_backend_deps():
    """Install Python dependencies"""
    print_step("4/8", "Installing backend dependencies...")
    
    pip_cmd = "backend\\venv\\Scripts\\pip" if os.name == 'nt' else "backend/venv/bin/pip"
    success, _, stderr = run_command(f"{pip_cmd} install -r backend/requirements.txt")
    
    if success:
        print_success("Backend dependencies installed")
        return True
    else:
        print_error(f"Failed to install dependencies: {stderr}")
        return False

def install_frontend_deps():
    """Install Node.js dependencies"""
    print_step("5/8", "Installing frontend dependencies...")
    
    if not Path("frontend/package.json").exists():
        print_warning("No package.json found, skipping")
        return True
    
    success, _, stderr = run_command("npm install", cwd="frontend")
    
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
    except Exception as e:
        print_error(f"PostgreSQL connection failed: {e}")
        print_warning("Make sure PostgreSQL is running on localhost:5432")
        print_warning("Default credentials: postgres / Abcd1234")
        return False

def create_database():
    """Create BQS database if it doesn't exist"""
    print_step("7/8", "Setting up database...")
    
    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
        # Connect to postgres database
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='Abcd1234',
            host='127.0.0.1',
            port=5432
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if bqs database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'bqs'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE bqs")
            print_success("Database 'bqs' created")
        else:
            print_success("Database 'bqs' already exists")
        
        cursor.close()
        conn.close()
        
        # Run schema migrations (create tables)
        print("  Running schema migrations...")
        sys.path.insert(0, 'backend')
        from database import init_db
        init_db()
        print_success("Tables created/verified")
        
        return True
        
    except Exception as e:
        print_error(f"Database setup failed: {e}")
        return False

def populate_data():
    """Populate test data"""
    print_step("8/8", "Populating test data...")
    
    python_cmd = "backend\\venv\\Scripts\\python" if os.name == 'nt' else "backend/venv/bin/python"
    success, stdout, stderr = run_command(f"{python_cmd} scripts/db_manager.py populate")
    
    if success:
        print_success("Test data populated")
        print(stdout)
        return True
    else:
        print_error(f"Data population failed: {stderr}")
        return False

def main():
    """Main setup process"""
    print("\n" + "="*70)
    print(f"{Colors.BOLD}🚀 BQS PROJECT SETUP{Colors.END}")
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
        ("Database", create_database),
    ]
    
    if with_data:
        steps.append(("Test Data", populate_data))
    
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
        print("     venv\\Scripts\\python main.py  (Windows)")
        print("     venv/bin/python main.py       (Mac/Linux)")
        print("\n  2. Start Frontend (new terminal):")
        print("     cd frontend")
        print("     npm run dev")
        print("\n  3. Open Browser:")
        print("     http://localhost:5173")
        
        if not with_data:
            print("\n💡 To populate test data:")
            print("     python scripts/db_manager.py populate")
        
        print("\n" + "="*70)
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ SETUP INCOMPLETE{Colors.END}")
        print("="*70)
        print(f"\nFailed steps: {', '.join(failed)}")
        print("\nPlease fix the errors above and run again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
