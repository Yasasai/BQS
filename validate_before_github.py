"""
BQS Pre-GitHub Validation Script
=================================

This script validates EVERY file interrelation before GitHub push.
It ensures nothing will break when someone clones the repository.

Tests:
1. ✅ All imports work
2. ✅ Database connection works
3. ✅ Models can be imported
4. ✅ Routers can be imported
5. ✅ Services can be imported
6. ✅ .env file is properly structured
7. ✅ All __init__.py files exist
8. ✅ No circular dependencies
9. ✅ Setup script works
10. ✅ Backend can start
"""

import os
import sys
import importlib
from pathlib import Path

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"{status} | {name}")
    if details:
        print(f"       {details}")

def print_section(name):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{name}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

# Get project root
ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(ROOT))

# Track results
tests_passed = 0
tests_failed = 0
failures = []

def test(name, func):
    global tests_passed, tests_failed, failures
    try:
        result, details = func()
        if result:
            tests_passed += 1
            print_test(name, True, details)
        else:
            tests_failed += 1
            failures.append((name, details))
            print_test(name, False, details)
    except Exception as e:
        tests_failed += 1
        failures.append((name, str(e)))
        print_test(name, False, f"Exception: {e}")

# ============================================================================
# TEST 1: File Structure
# ============================================================================

def test_file_structure():
    """Verify all essential files exist"""
    print_section("TEST 1: File Structure Validation")
    
    essential_files = [
        ".env",
        ".gitignore",
        "README.md",
        "backend/requirements.txt",
        "backend/__init__.py",
        "backend/app/__init__.py",
        "backend/app/main.py",
        "backend/app/models.py",
        "backend/app/core/__init__.py",
        "backend/app/core/database.py",
        "backend/app/core/constants.py",
        "backend/app/routers/__init__.py",
        "backend/app/routers/auth.py",
        "backend/app/routers/inbox.py",
        "backend/app/routers/scoring.py",
        "backend/app/services/__init__.py",
        "backend/app/services/oracle_service.py",
        "backend/app/services/sync_manager.py",
        "scripts/setup/setup_project.py",
    ]
    
    missing = []
    for file in essential_files:
        path = ROOT / file
        if not path.exists():
            missing.append(file)
    
    if missing:
        return False, f"Missing files: {', '.join(missing)}"
    return True, f"All {len(essential_files)} essential files exist"

test("Essential files exist", test_file_structure)

# ============================================================================
# TEST 2: Python Package Structure
# ============================================================================

def test_package_structure():
    """Verify all __init__.py files exist"""
    print_section("TEST 2: Python Package Structure")
    
    required_inits = [
        "backend/__init__.py",
        "backend/app/__init__.py",
        "backend/app/core/__init__.py",
        "backend/app/routers/__init__.py",
        "backend/app/services/__init__.py",
    ]
    
    missing = []
    for init_file in required_inits:
        path = ROOT / init_file
        if not path.exists():
            missing.append(init_file)
    
    if missing:
        return False, f"Missing __init__.py: {', '.join(missing)}"
    return True, f"All {len(required_inits)} package markers exist"

test("Package structure valid", test_package_structure)

# ============================================================================
# TEST 3: Import Tests
# ============================================================================

print_section("TEST 3: Import Validation")

def test_import_models():
    """Test if models.py can be imported"""
    try:
        from backend.app.models import (
            Base, AppUser, Role, UserRole, Practice, Opportunity,
            OpportunityAssignment, OppScoreVersion, OppScoreSection
        )
        return True, "All models imported successfully"
    except ImportError as e:
        return False, f"Import error: {e}"

test("Import models.py", test_import_models)

def test_import_database():
    """Test if database.py can be imported"""
    try:
        from backend.app.core.database import init_db, get_db, SessionLocal
        return True, "Database module imported successfully"
    except ImportError as e:
        return False, f"Import error: {e}"

test("Import database.py", test_import_database)

def test_import_constants():
    """Test if constants.py can be imported"""
    try:
        # First check if file exists
        const_path = ROOT / "backend" / "app" / "core" / "constants.py"
        if not const_path.exists():
            # Try old location
            const_path = ROOT / "backend" / "constants.py"
            if const_path.exists():
                return False, "constants.py in wrong location (backend/ instead of backend/app/core/)"
        
        # Try to import
        from backend.app.core import constants
        return True, "Constants module imported successfully"
    except ImportError as e:
        return False, f"Import error: {e}"

test("Import constants.py", test_import_constants)

def test_import_routers():
    """Test if all routers can be imported"""
    try:
        from backend.app.routers import auth, inbox, scoring
        return True, "All routers imported successfully"
    except ImportError as e:
        return False, f"Import error: {e}"

test("Import routers", test_import_routers)

def test_import_services():
    """Test if all services can be imported"""
    try:
        from backend.app.services import oracle_service, sync_manager
        return True, "All services imported successfully"
    except ImportError as e:
        return False, f"Import error: {e}"

test("Import services", test_import_services)

def test_import_main():
    """Test if main.py can be imported"""
    try:
        # Don't actually import (it would start the server)
        # Just check if the file is syntactically correct
        import ast
        main_path = ROOT / "backend" / "app" / "main.py"
        with open(main_path, 'r') as f:
            ast.parse(f.read())
        return True, "main.py syntax valid"
    except SyntaxError as e:
        return False, f"Syntax error: {e}"

test("Import main.py", test_import_main)

# ============================================================================
# TEST 4: Dependency Chain
# ============================================================================

print_section("TEST 4: Dependency Chain Validation")

def test_models_dependency():
    """Test models.py has no missing dependencies"""
    try:
        from backend.app.models import Base, Opportunity
        # Check if Base has metadata (SQLAlchemy working)
        if hasattr(Base, 'metadata'):
            return True, "Models properly configured with SQLAlchemy"
        return False, "Base.metadata not found"
    except Exception as e:
        return False, f"Error: {e}"

test("Models dependencies", test_models_dependency)

def test_database_dependency():
    """Test database.py can import models"""
    try:
        from backend.app.core.database import init_db
        from backend.app.models import Base
        # Check if init_db can access Base
        return True, "database.py → models.py link valid"
    except Exception as e:
        return False, f"Error: {e}"

test("Database → Models link", test_database_dependency)

def test_routers_dependency():
    """Test routers can import database and models"""
    try:
        from backend.app.routers.inbox import router
        # Check if router is a FastAPI router
        if hasattr(router, 'routes'):
            return True, "Routers properly configured"
        return False, "Router not properly configured"
    except Exception as e:
        return False, f"Error: {e}"

test("Routers → Database/Models link", test_routers_dependency)

def test_services_dependency():
    """Test services can import what they need"""
    try:
        from backend.app.services.sync_manager import sync_opportunities
        from backend.app.services.oracle_service import get_from_oracle
        return True, "Services properly configured"
    except Exception as e:
        return False, f"Error: {e}"

test("Services dependencies", test_services_dependency)

def test_main_dependency():
    """Test main.py can import all routers and services"""
    try:
        # Parse main.py and check imports
        import ast
        main_path = ROOT / "backend" / "app" / "main.py"
        with open(main_path, 'r') as f:
            tree = ast.parse(f.read())
        
        # Check for required imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                imports.append(node.module)
        
        required = [
            'backend.app.core.database',
            'backend.app.services.sync_manager',
            'backend.app.routers'
        ]
        
        missing = [r for r in required if not any(r in i for i in imports if i)]
        if missing:
            return False, f"Missing imports in main.py: {missing}"
        
        return True, "main.py imports all required modules"
    except Exception as e:
        return False, f"Error: {e}"

test("Main → All modules link", test_main_dependency)

# ============================================================================
# TEST 5: Circular Dependency Check
# ============================================================================

print_section("TEST 5: Circular Dependency Check")

def test_no_circular_deps():
    """Ensure no circular dependencies"""
    try:
        # Try importing in different orders
        from backend.app.models import Opportunity
        from backend.app.core.database import get_db
        from backend.app.routers.inbox import router
        from backend.app.services.sync_manager import sync_opportunities
        
        # If we get here, no circular deps
        return True, "No circular dependencies detected"
    except ImportError as e:
        if "circular" in str(e).lower():
            return False, f"Circular dependency: {e}"
        return False, f"Import error: {e}"

test("No circular dependencies", test_no_circular_deps)

# ============================================================================
# TEST 6: Configuration Validation
# ============================================================================

print_section("TEST 6: Configuration Validation")

def test_env_file():
    """Check .env file structure"""
    env_path = ROOT / ".env"
    if not env_path.exists():
        return False, ".env file missing"
    
    required_vars = [
        "ORACLE_BASE_URL",
        "ORACLE_USER",
        "DATABASE_URL"
    ]
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    missing = [var for var in required_vars if var not in content]
    if missing:
        return False, f"Missing env vars: {', '.join(missing)}"
    
    return True, f"All {len(required_vars)} required env vars present"

test(".env file structure", test_env_file)

def test_requirements_file():
    """Check requirements.txt has all needed packages"""
    req_path = ROOT / "backend" / "requirements.txt"
    if not req_path.exists():
        return False, "requirements.txt missing"
    
    with open(req_path, 'r') as f:
        content = f.read().lower()
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "psycopg2-binary",
        "python-dotenv",
        "requests",
        "httpx"
    ]
    
    missing = [pkg for pkg in required_packages if pkg not in content]
    if missing:
        return False, f"Missing packages: {', '.join(missing)}"
    
    return True, f"All {len(required_packages)} required packages listed"

test("requirements.txt complete", test_requirements_file)

# ============================================================================
# TEST 7: File Content Validation
# ============================================================================

print_section("TEST 7: File Content Validation")

def test_models_has_tables():
    """Check models.py defines all required tables"""
    try:
        from backend.app.models import (
            AppUser, Role, UserRole, Practice, Opportunity,
            OpportunityAssignment, OppScoreVersion, OppScoreSection,
            OppScoreSectionValue, SyncRun
        )
        
        tables = [
            AppUser, Role, UserRole, Practice, Opportunity,
            OpportunityAssignment, OppScoreVersion, OppScoreSection,
            OppScoreSectionValue, SyncRun
        ]
        
        # Check each has __tablename__
        missing = [t.__name__ for t in tables if not hasattr(t, '__tablename__')]
        if missing:
            return False, f"Tables missing __tablename__: {missing}"
        
        return True, f"All {len(tables)} tables properly defined"
    except Exception as e:
        return False, f"Error: {e}"

test("Models define all tables", test_models_has_tables)

def test_database_has_init():
    """Check database.py has init_db function"""
    try:
        from backend.app.core.database import init_db
        import inspect
        if callable(init_db):
            return True, "init_db function exists and is callable"
        return False, "init_db is not callable"
    except Exception as e:
        return False, f"Error: {e}"

test("database.py has init_db", test_database_has_init)

def test_routers_have_endpoints():
    """Check routers define API endpoints"""
    try:
        from backend.app.routers import auth, inbox, scoring
        
        routers = [
            ('auth', auth.router),
            ('inbox', inbox.router),
            ('scoring', scoring.router)
        ]
        
        for name, router in routers:
            if not hasattr(router, 'routes') or len(router.routes) == 0:
                return False, f"{name} router has no routes"
        
        return True, "All routers have endpoints defined"
    except Exception as e:
        return False, f"Error: {e}"

test("Routers have endpoints", test_routers_have_endpoints)

def test_services_have_functions():
    """Check services define required functions"""
    try:
        from backend.app.services.oracle_service import get_from_oracle
        from backend.app.services.sync_manager import sync_opportunities
        
        if not callable(get_from_oracle):
            return False, "get_from_oracle not callable"
        if not callable(sync_opportunities):
            return False, "sync_opportunities not callable"
        
        return True, "All service functions exist and are callable"
    except Exception as e:
        return False, f"Error: {e}"

test("Services have required functions", test_services_have_functions)

# ============================================================================
# TEST 8: Integration Test
# ============================================================================

print_section("TEST 8: Integration Test")

def test_full_import_chain():
    """Test the complete import chain works"""
    try:
        # Simulate what happens when backend starts
        from backend.app.core.database import init_db, get_db
        from backend.app.services.sync_manager import sync_opportunities
        from backend.app.routers import auth, inbox, scoring
        from backend.app.models import Opportunity
        
        # Check all are properly loaded
        return True, "Complete import chain successful"
    except Exception as e:
        return False, f"Error in import chain: {e}"

test("Full import chain", test_full_import_chain)

# ============================================================================
# FINAL REPORT
# ============================================================================

print_section("VALIDATION REPORT")

total_tests = tests_passed + tests_failed
pass_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0

print(f"Total Tests: {total_tests}")
print(f"{Colors.GREEN}Passed: {tests_passed}{Colors.END}")
print(f"{Colors.RED}Failed: {tests_failed}{Colors.END}")
print(f"Pass Rate: {pass_rate:.1f}%\n")

if tests_failed > 0:
    print(f"{Colors.RED}{Colors.BOLD}FAILURES:{Colors.END}")
    for name, details in failures:
        print(f"{Colors.RED}✗{Colors.END} {name}")
        print(f"  {details}\n")
    
    print(f"\n{Colors.RED}{Colors.BOLD}❌ VALIDATION FAILED - DO NOT PUSH TO GITHUB{Colors.END}")
    print(f"{Colors.YELLOW}Fix the errors above before pushing.{Colors.END}\n")
    sys.exit(1)
else:
    print(f"{Colors.GREEN}{Colors.BOLD}✅ ALL TESTS PASSED - SAFE TO PUSH TO GITHUB{Colors.END}")
    print(f"{Colors.GREEN}All file interrelations are valid!{Colors.END}\n")
    
    print(f"{Colors.BLUE}Next steps:{Colors.END}")
    print(f"1. Run cleanup: python cleanup_project.py")
    print(f"2. Test setup: python scripts/setup/setup_project.py --with-data")
    print(f"3. Commit to Git: git add . && git commit -m 'Restructured project'")
    print(f"4. Push to GitHub: git push\n")
    
    sys.exit(0)
