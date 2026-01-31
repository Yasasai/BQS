"""
BQS Automated Cleanup Script
=============================

This script safely removes duplicate and obsolete files while preserving
the essential modular structure.

WHAT IT DOES:
1. Creates a backup folder (BQS_BACKUP_[timestamp])
2. Backs up files before deletion
3. Removes obsolete files from root and backend
4. Moves useful debugging scripts to scripts/util
5. Generates a cleanup report

SAFETY: All deleted files are backed up first!
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

# Color codes for terminal
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

# Get project root
ROOT = Path(__file__).parent.absolute()
BACKUP_DIR = ROOT / f"BQS_BACKUP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Files to DELETE from root directory
ROOT_DELETE = [
    "requirements.txt",
    "check_backend.py",
    "check_data.py",
    "create_env.py",
    "database_dump.json",
    "db_check_fast.py",
    "debug_oracle.py",
    "diagnose_sync.py",
    "diagnostic.py",
    "direct_api_test.py",
    "extract_names.py",
    "fetch_all_methods.py",
    "fetch_by_names.py",
    "final_status_check.py",
    "find_oracle_url.py",
    "fix_dotenv_finally.py",
    "fix_install.bat",
    "heal_database.py",
    "oracle_api_config.txt",
    "populate_test_data.py",
    "prepare_github.bat",
    "probe_fields.py",
    "push_all.bat",
    "quick_db_probe.py",
    "quick_populate.py",
    "quick_verify_fix.py",
    "refined_sync_script.py",
    "run_manual_sync.bat",
    "run_sync.bat",
    "run_sync_now.bat",
    "seed_screenshot.py",
    "self_heal.py",
    "setup_complete.bat",
    "setup_complete.py",
    "setup_data.bat",
    "setup_env.bat",
    "setup_now.py",
    "simple_sync.py",
    "standardize_env.py",
    "sync_control_panel.html",
    "test_direct_oracle.py",
    "test_oracle_connection.py",
    "test_oracle_data.py",
    "test_oracle_permissions.py",
    "trigger_sync.py",
    "trigger_sync_now.bat",
    "update_env_aliases.py",
    "verify_details.py",
    "verify_env.py",
    "SYNC_NOW.bat",
]

# Files to DELETE from backend directory
BACKEND_DELETE = [
    "auto_heal.py",
    "constants.py",
    "database.py",
    "dump_data.py",
    "inspect_oracle_fields.py",
    "main.py",
    "migrate_db.py",
    "oracle_service.py",
    "populate_dummy_data.py",
    "quick_populate.py",
    "restore_data.py",
    "run_populate.bat",
    "start_backend.bat",
    "sync_manager.py",
    "sync_status.py",
    "test_imports.py",
]

# Directories to DELETE from backend
BACKEND_DELETE_DIRS = [
    "routers",  # Old routers folder (replaced by app/routers)
]

# Documentation files to DELETE (will be consolidated)
DOC_DELETE = [
    "CLEANUP.md",
    "EMERGENCY_GUIDE.md",
    "GITHUB_PUSH_CHECKLIST.md",
    "GITHUB_PUSH_GUIDE.md",
    "IMMEDIATE_SYNC_GUIDE.md",
    "IMPLEMENTATION_SUMMARY.md",
    "ORACLE_SYNC_GUIDE.md",
    "PUSH_SUMMARY.md",
    "SELF_HEAL.txt",
    "SETUP_GUIDE.md",
    "SQLALCHEMY_FIX.md",
    "SYNC_QUICKSTART.md",
    "TROUBLESHOOTING_TIMEOUT.md",
]

# Files to MOVE to scripts/util (useful for debugging)
MOVE_TO_UTIL = {
    "debug_oracle.py": "scripts/util/debug_oracle.py",
    "diagnose_sync.py": "scripts/util/diagnose_sync.py",
    "test_oracle_connection.py": "scripts/util/test_oracle_connection.py",
    "backend/dump_data.py": "scripts/util/dump_data.py",
    "backend/restore_data.py": "scripts/util/restore_data.py",
}

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓{Colors.END} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠{Colors.END} {text}")

def print_error(text):
    print(f"{Colors.RED}✗{Colors.END} {text}")

def create_backup():
    """Create backup directory"""
    print_header("STEP 1: Creating Backup")
    
    try:
        BACKUP_DIR.mkdir(exist_ok=True)
        print_success(f"Backup directory created: {BACKUP_DIR.name}")
        return True
    except Exception as e:
        print_error(f"Failed to create backup: {e}")
        return False

def backup_and_delete_files(file_list, base_path, category_name):
    """Backup and delete files from a specific directory"""
    print_header(f"STEP: Cleaning {category_name}")
    
    deleted_count = 0
    skipped_count = 0
    
    for filename in file_list:
        file_path = base_path / filename
        
        if file_path.exists():
            try:
                # Create backup
                backup_path = BACKUP_DIR / category_name / filename
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                
                if file_path.is_file():
                    shutil.copy2(file_path, backup_path)
                    file_path.unlink()
                    print_success(f"Deleted: {filename}")
                    deleted_count += 1
                elif file_path.is_dir():
                    shutil.copytree(file_path, backup_path, dirs_exist_ok=True)
                    shutil.rmtree(file_path)
                    print_success(f"Deleted directory: {filename}")
                    deleted_count += 1
                    
            except Exception as e:
                print_error(f"Failed to delete {filename}: {e}")
                skipped_count += 1
        else:
            skipped_count += 1
    
    print(f"\n{Colors.BOLD}Summary:{Colors.END} Deleted {deleted_count}, Skipped {skipped_count}")
    return deleted_count

def move_files():
    """Move useful files to scripts/util"""
    print_header("STEP: Moving Utility Scripts")
    
    moved_count = 0
    
    for src_rel, dst_rel in MOVE_TO_UTIL.items():
        src = ROOT / src_rel
        dst = ROOT / dst_rel
        
        if src.exists():
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                print_success(f"Moved: {src_rel} → {dst_rel}")
                moved_count += 1
            except Exception as e:
                print_error(f"Failed to move {src_rel}: {e}")
    
    print(f"\n{Colors.BOLD}Summary:{Colors.END} Moved {moved_count} files")
    return moved_count

def generate_report(stats):
    """Generate cleanup report"""
    print_header("CLEANUP REPORT")
    
    report_path = ROOT / "CLEANUP_REPORT.txt"
    
    with open(report_path, 'w') as f:
        f.write("BQS PROJECT CLEANUP REPORT\n")
        f.write("=" * 70 + "\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Backup Location: {BACKUP_DIR.name}\n\n")
        
        f.write("STATISTICS:\n")
        f.write(f"  Root files deleted: {stats['root']}\n")
        f.write(f"  Backend files deleted: {stats['backend']}\n")
        f.write(f"  Documentation deleted: {stats['docs']}\n")
        f.write(f"  Files moved to util: {stats['moved']}\n")
        f.write(f"  Total files removed: {stats['total']}\n\n")
        
        f.write("REMAINING STRUCTURE:\n")
        f.write("  backend/app/          - Main application code\n")
        f.write("  backend/app/core/     - Database & constants\n")
        f.write("  backend/app/routers/  - API endpoints\n")
        f.write("  backend/app/services/ - Oracle & sync logic\n")
        f.write("  frontend/             - React application\n")
        f.write("  scripts/setup/        - Setup scripts\n")
        f.write("  scripts/util/         - Debugging utilities\n")
        f.write("  doc/                  - Documentation\n\n")
        
        f.write("NEXT STEPS:\n")
        f.write("  1. Review the cleanup (check BACKUP folder if needed)\n")
        f.write("  2. Run: python scripts/setup/setup_project.py --with-data\n")
        f.write("  3. Test the application\n")
        f.write("  4. If everything works, delete the BACKUP folder\n")
        f.write("  5. Commit changes to Git\n")
    
    print_success(f"Report saved: {report_path.name}")
    
    print(f"\n{Colors.BOLD}STATISTICS:{Colors.END}")
    print(f"  Root files deleted: {stats['root']}")
    print(f"  Backend files deleted: {stats['backend']}")
    print(f"  Documentation deleted: {stats['docs']}")
    print(f"  Files moved to util: {stats['moved']}")
    print(f"  {Colors.GREEN}Total files removed: {stats['total']}{Colors.END}")

def main():
    """Main cleanup process"""
    print_header("🧹 BQS PROJECT CLEANUP")
    print("This script will clean up duplicate and obsolete files.")
    print("All files will be backed up before deletion.\n")
    
    response = input(f"{Colors.YELLOW}Continue with cleanup? (yes/no): {Colors.END}").strip().lower()
    
    if response != 'yes':
        print_warning("Cleanup cancelled by user.")
        return
    
    # Create backup
    if not create_backup():
        print_error("Backup failed. Aborting cleanup.")
        return
    
    # Track statistics
    stats = {
        'root': 0,
        'backend': 0,
        'docs': 0,
        'moved': 0,
        'total': 0
    }
    
    # Clean root directory
    stats['root'] = backup_and_delete_files(ROOT_DELETE, ROOT, "root")
    
    # Clean backend directory
    backend_path = ROOT / "backend"
    stats['backend'] = backup_and_delete_files(
        BACKEND_DELETE + BACKEND_DELETE_DIRS, 
        backend_path, 
        "backend"
    )
    
    # Clean documentation
    stats['docs'] = backup_and_delete_files(DOC_DELETE, ROOT, "docs")
    
    # Move utility files
    stats['moved'] = move_files()
    
    # Calculate total
    stats['total'] = stats['root'] + stats['backend'] + stats['docs']
    
    # Generate report
    generate_report(stats)
    
    print_header("✅ CLEANUP COMPLETE!")
    print(f"Backup saved to: {Colors.BOLD}{BACKUP_DIR.name}{Colors.END}")
    print(f"\nNext: Run {Colors.BOLD}python scripts/setup/setup_project.py --with-data{Colors.END}")

if __name__ == "__main__":
    main()
