# -*- coding: utf-8 -*-
"""
Phase 4.5 Hotfix Seed Script
============================
Populates the app_user, role, and user_role tables with real test users
so the frontend can authenticate against the live PostgreSQL database.

Email addresses match the MOCK_USERS table in frontend/src/context/AuthContext.tsx
so that both the initial role-picker login AND the sidebar user-switcher work.

Run from the backend folder:
    cd backend
    python seed_users.py
"""

import sys
import os

# ---------------------------------------------------------------------------
# Path bootstrap: make sure both project root AND backend/ are importable
# ---------------------------------------------------------------------------
this_dir = os.path.dirname(os.path.abspath(__file__))   # .../BQS/backend
project_root = os.path.dirname(this_dir)                 # .../BQS
for path in [this_dir, project_root]:
    if path not in sys.path:
        sys.path.insert(0, path)

from dotenv import load_dotenv
load_dotenv(os.path.join(this_dir, ".env"))              # load backend/.env

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models import AppUser, Role, UserRole, Base

# ---------------------------------------------------------------------------
# Database connection (reads DATABASE_URL from .env)
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Check backend/.env")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ---------------------------------------------------------------------------
# Seed data  --  emails MUST match MOCK_USERS in AuthContext.tsx
# ---------------------------------------------------------------------------
ROLES_DATA = [
    {"role_id": 1, "role_code": "GH", "role_name": "Global Head"},
    {"role_id": 2, "role_code": "PH", "role_name": "Practice Head"},
    {"role_id": 3, "role_code": "SH", "role_name": "Sales Head"},
    {"role_id": 4, "role_code": "SA", "role_name": "Solution Architect"},
    {"role_id": 5, "role_code": "SP", "role_name": "Sales Person"},
    {"role_id": 6, "role_code": "LEGAL", "role_name": "Legal Head"},
    {"role_id": 7, "role_code": "FINANCE", "role_name": "Finance Head"},
]

USERS_DATA = [
    # Global Heads
    {"user_id": "gh-001", "email": "james.wilson@inspiraenterprise.com",
     "display_name": "James Wilson",          "role_code": "GH"},
    {"user_id": "gh-002", "email": "maria.garcia@inspiraenterprise.com",
     "display_name": "Maria Garcia",          "role_code": "GH"},

    # Practice Heads
    {"user_id": "ph-001", "email": "sarah.mitchell@inspiraenterprise.com",
     "display_name": "Sarah Mitchell",        "role_code": "PH"},
    {"user_id": "ph-002", "email": "david.chen@inspiraenterprise.com",
     "display_name": "David Chen",            "role_code": "PH"},
    {"user_id": "ph-003", "email": "priya.sharma@inspiraenterprise.com",
     "display_name": "Priya Sharma",          "role_code": "PH"},
    {"user_id": "ph-004", "email": "michael.brown@inspiraenterprise.com",
     "display_name": "Michael Brown",         "role_code": "PH"},
    {"user_id": "ph-005", "email": "lisa.anderson@inspiraenterprise.com",
     "display_name": "Lisa Anderson",         "role_code": "PH"},

    # Sales Heads
    {"user_id": "sh-001", "email": "robert.chen@inspiraenterprise.com",
     "display_name": "Robert Chen",           "role_code": "SH"},
    {"user_id": "sh-002", "email": "jennifer.lee@inspiraenterprise.com",
     "display_name": "Jennifer Lee",          "role_code": "SH"},
    {"user_id": "sh-003", "email": "alex.kumar@inspiraenterprise.com",
     "display_name": "Alex Kumar",            "role_code": "SH"},
    {"user_id": "sh-004", "email": "emma.johnson@inspiraenterprise.com",
     "display_name": "Emma Johnson",          "role_code": "SH"},
    {"user_id": "sh-005", "email": "kunal.sales@inspiraenterprise.com",
     "display_name": "Kunal Sales Lead",      "role_code": "SH"},

    # Solution Architects
    # sa-000 matches MOCK_USERS['SA'] in AuthContext.tsx exactly
    {"user_id": "sa-000", "email": "john.architect@inspiraenterprise.com",
     "display_name": "John Architect",        "role_code": "SA"},
    {"user_id": "sa-001", "email": "john.doe@inspiraenterprise.com",
     "display_name": "John Doe",              "role_code": "SA"},
    {"user_id": "sa-002", "email": "alice.wong@inspiraenterprise.com",
     "display_name": "Alice Wong",            "role_code": "SA"},
    {"user_id": "sa-003", "email": "raj.patel@inspiraenterprise.com",
     "display_name": "Raj Patel",             "role_code": "SA"},
    {"user_id": "sa-004", "email": "sophia.martinez@inspiraenterprise.com",
     "display_name": "Sophia Martinez",       "role_code": "SA"},
    {"user_id": "sa-005", "email": "thomas.wright@inspiraenterprise.com",
     "display_name": "Thomas Wright",         "role_code": "SA"},
    {"user_id": "sa-006", "email": "olivia.taylor@inspiraenterprise.com",
     "display_name": "Olivia Taylor",         "role_code": "SA"},

    # Salespersons
    # sp-000 matches MOCK_USERS['SP'] in AuthContext.tsx exactly
    {"user_id": "sp-000", "email": "emily.sales@inspiraenterprise.com",
     "display_name": "Emily Sales",           "role_code": "SP"},
    {"user_id": "sp-001", "email": "emily.white@inspiraenterprise.com",
     "display_name": "Emily White",           "role_code": "SP"},
    {"user_id": "sp-002", "email": "daniel.kim@inspiraenterprise.com",
     "display_name": "Daniel Kim",            "role_code": "SP"},
    {"user_id": "sp-003", "email": "natalie.rodriguez@inspiraenterprise.com",
     "display_name": "Natalie Rodriguez",     "role_code": "SP"},
    {"user_id": "sp-004", "email": "kevin.nguyen@inspiraenterprise.com",
     "display_name": "Kevin Nguyen",          "role_code": "SP"},
    {"user_id": "sp-005", "email": "hannah.davis@inspiraenterprise.com",
     "display_name": "Hannah Davis",          "role_code": "SP"},

    # Legal
    {"user_id": "legal-001", "email": "legal.one@inspiraenterprise.com",
     "display_name": "Legal Lead Officer",    "role_code": "LEGAL"},
    {"user_id": "legal-002", "email": "legal.two@inspiraenterprise.com",
     "display_name": "Legal Lead Assistant",  "role_code": "LEGAL"},

    # Finance
    {"user_id": "finance-001", "email": "finance.one@inspiraenterprise.com",
     "display_name": "Finance Lead Manager", "role_code": "FINANCE"},
    {"user_id": "finance-002", "email": "finance.two@inspiraenterprise.com",
     "display_name": "Finance Controller",   "role_code": "FINANCE"},

    # Specific Legal Leads requested by user
    {"user_id": "21", "email": "legal1@company.com", "display_name": "Amit Sharma - Legal", "role_code": "LEGAL"},
    {"user_id": "22", "email": "legal2@company.com", "display_name": "Priya Menon - Legal", "role_code": "LEGAL"},
    {"user_id": "23", "email": "legal3@company.com", "display_name": "Rohit Gupta - Legal", "role_code": "LEGAL"},
]


def seed():
    """Idempotently create tables and populate users + roles."""
    print("=== BQS Phase 4.5 Hotfix - Seed Script ===")
    print("DATABASE_URL:", DATABASE_URL[:40] + "..." if DATABASE_URL and len(DATABASE_URL) > 40 else DATABASE_URL)

    # Create all tables (no-op if already exist)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # ---- 1. Roles -------------------------------------------------------
        print("\n[ROLES]")
        for rd in ROLES_DATA:
            role = db.query(Role).filter(Role.role_code == rd["role_code"]).first()
            if not role:
                db.add(Role(**rd))
                print("  + Created: {}".format(rd["role_name"]))
            else:
                print("  . Exists:  {}".format(rd["role_name"]))
        db.commit()

        # ---- 2. Users -------------------------------------------------------
        print("\n[USERS]")
        for ud in USERS_DATA:
            # Check by user_id first; fall back to email to prevent duplicate violations
            user = (
                db.query(AppUser).filter(AppUser.user_id == ud["user_id"]).first()
                or db.query(AppUser).filter(AppUser.email  == ud["email"]).first()
            )
            if not user:
                user = AppUser(
                    user_id=ud["user_id"],
                    email=ud["email"],
                    display_name=ud["display_name"],
                    is_active=True,
                )
                db.add(user)
                db.flush()
                print("  + Created: {} <{}>  [{}]".format(
                    ud["display_name"], ud["email"], ud["role_code"]))
            else:
                # Ensure account is active and email is in sync
                user.is_active = True
                user.email = ud["email"]
                print("  ~ Updated: {} <{}>".format(ud["display_name"], ud["email"]))

            # ---- 3. Role assignment -----------------------------------------
            role = db.query(Role).filter(Role.role_code == ud["role_code"]).first()
            if role:
                exists = db.query(UserRole).filter(
                    UserRole.user_id == user.user_id,
                    UserRole.role_id == role.role_id,
                ).first()
                if not exists:
                    db.add(UserRole(user_id=user.user_id, role_id=role.role_id))
                    print("         -> Assigned role: {}".format(ud["role_code"]))

        db.commit()

        # ---- 4. Summary -----------------------------------------------------
        print("\n" + "=" * 54)
        print("SUMMARY")
        print("=" * 54)
        for rd in ROLES_DATA:
            role = db.query(Role).filter(Role.role_code == rd["role_code"]).first()
            count = (
                db.query(UserRole).filter(UserRole.role_id == role.role_id).count()
                if role else 0
            )
            print("  {:<30} : {} user(s)".format(rd["role_name"], count))
        total = db.query(AppUser).filter(AppUser.is_active == True).count()
        print("  {:<30} : {} user(s)".format("TOTAL ACTIVE", total))
        print("=" * 54)

        print("\nSeeding complete!")
        print("\nQuick-login credentials (email-only auth):")
        print("  Global Head        -> james.wilson@inspiraenterprise.com")
        print("  Practice Head      -> sarah.mitchell@inspiraenterprise.com")
        print("  Sales Head         -> robert.chen@inspiraenterprise.com")
        print("  Solution Architect -> john.architect@inspiraenterprise.com")
        print("  Sales Person       -> emily.sales@inspiraenterprise.com")
        print("")

    except Exception as exc:
        db.rollback()
        print("\nERROR: Seeding failed: {}".format(exc))
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
