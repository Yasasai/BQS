# -*- coding: utf-8 -*-
"""
Phase 4.6 Hotfix - Seed Opportunities
======================================
Populates the `opportunity` table using the correct SQLAlchemy models
so that all dashboard screens show real data.

Users seeded by seed_users.py are used as owners/assignees for realism.

Run from the backend folder:
    cd backend
    python seed_opportunities.py
"""

import sys
import os
import uuid
import random
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------------------
# Path bootstrap
# ---------------------------------------------------------------------------
this_dir = os.path.dirname(os.path.abspath(__file__))   # .../BQS/backend
project_root = os.path.dirname(this_dir)                 # .../BQS
for path in [this_dir, project_root]:
    if path not in sys.path:
        sys.path.insert(0, path)

from dotenv import load_dotenv
load_dotenv(os.path.join(this_dir, ".env"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models import (
    AppUser, Role, UserRole, Practice, Opportunity,
    OppScoreVersion, OppScoreSectionValue, OppScoreSection, Base
)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Check backend/.env")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def now():
    return datetime.now(timezone.utc)

def rand_date(days_ahead_min=30, days_ahead_max=180):
    return now() + timedelta(days=random.randint(days_ahead_min, days_ahead_max))

def rand_value():
    return round(random.uniform(500_000, 15_000_000), 2)

# ---------------------------------------------------------------------------
# Opportunity seed data
# ---------------------------------------------------------------------------
CUSTOMERS = [
    "JPMorgan Chase", "FedEx Logistics", "Coca-Cola Enterprises",
    "Tesla Energy", "Apple EMEA", "Google Cloud", "Amazon Web Services",
    "Netflix Studios", "Microsoft Azure", "Samsung Electronics",
    "HSBC Banking", "Siemens AG", "Oracle Corp", "SAP SE", "Accenture",
    "Deloitte Advisory", "Goldman Sachs", "UnitedHealth Group", "Pfizer Ltd", "Boeing"
]

GEO_LIST = ["APAC", "EMEA", "NAMER", "LATAM", "MEA"]

STAGES = [
    "1. Prospect", "2. Develop", "3. Qualify", "4. Commit", "5. Closed Won"
]

# Workflow statuses that the UI understands
WORKFLOW_STATUSES = [
    "NEW_FROM_CRM",          # Management Dashboard - unassigned inbox
    "ASSIGNED_TO_SA",        # SA Dashboard - assigned
    "UNDER_ASSESSMENT",      # SA Dashboard - in progress
    "WAITING_PH_APPROVAL",   # PH Dashboard - pending review
    "READY_FOR_MGMT_REVIEW", # GH Dashboard - awaiting management approval
    "APPROVED",              # Completed - bid approved
    "REJECTED",              # Completed - bid rejected
]

PRACTICE_NAMES = [
    ("CLOUD", "Cloud & Infrastructure"),
    ("CYBER", "Cybersecurity"),
    ("DATA",  "Data & Analytics"),
    ("AI_ML", "AI & Machine Learning"),
    ("ERP",   "Enterprise ERP"),
    ("NET",   "Networking"),
    ("SOFT",  "Software Engineering"),
]

# ---------------------------------------------------------------------------
# Main seed function
# ---------------------------------------------------------------------------
def seed_opportunities():
    print("=" * 65)
    print("  BQS Phase 4.6 Hotfix - Opportunity Seeder")
    print("=" * 65)

    Base.metadata.create_all(bind=engine)  # ensure tables exist
    db = SessionLocal()

    try:
        # ---- 0. Check users exist ----------------------------------------
        users_by_role: dict[str, list] = {}
        for role_code in ["GH", "PH", "SH", "SA", "SP"]:
            role = db.query(Role).filter(Role.role_code == role_code).first()
            if not role:
                print(f"  ⚠  Role '{role_code}' not found. Run seed_users.py first!")
                db.close()
                return
            assigned = (
                db.query(AppUser)
                .join(UserRole, AppUser.user_id == UserRole.user_id)
                .filter(UserRole.role_id == role.role_id)
                .all()
            )
            users_by_role[role_code] = assigned
            print(f"  ✓  Found {len(assigned)} {role_code} user(s)")

        # ---- 1. Practices ---------------------------------------------------
        print("\n[1/3] Ensuring practices exist...")
        practice_map: dict[str, str] = {}  # name -> practice_id
        for code, name in PRACTICE_NAMES:
            p = db.query(Practice).filter(Practice.practice_name == name).first()
            if not p:
                p = Practice(
                    practice_id=str(uuid.uuid4()),
                    practice_code=code[:20],
                    practice_name=name,
                )
                db.add(p)
                db.flush()
                print(f"    + Created: {name}")
            else:
                print(f"    . Exists:  {name}")
            practice_map[name] = p.practice_id
        db.commit()

        # ---- 2. Check existing opportunities --------------------------------
        existing_count = db.query(Opportunity).count()
        print(f"\n[2/3] Current opportunity count: {existing_count}")
        if existing_count >= 30:
            print("  ✅  Already have enough opportunities - skipping seed.")
            print(f"     (Delete from the opportunity table to re-seed)")
            db.close()
            return

        # ---- 3. Insert opportunities ----------------------------------------
        print("\n[3/3] Generating 30 realistic opportunities...")

        sa_list   = users_by_role.get("SA", [])
        sh_list   = users_by_role.get("SH", [])
        ph_list   = users_by_role.get("PH", [])
        gh_list   = users_by_role.get("GH", [])
        sp_list   = users_by_role.get("SP", [])

        # Distribution: 5 per status (but spread across 7 statuses → ~4-5 each)
        status_pool = WORKFLOW_STATUSES * 5  # 35 items
        random.shuffle(status_pool)
        status_pool = status_pool[:30]

        inserted = 0
        for i, wf_status in enumerate(status_pool):
            customer   = CUSTOMERS[i % len(CUSTOMERS)]
            geo        = random.choice(GEO_LIST)
            practice_n = random.choice(PRACTICE_NAMES)[1]
            practice_id = practice_map.get(practice_n)
            stage      = random.choice(STAGES)
            deal_value = rand_value()
            crm_ts     = now() - timedelta(days=random.randint(1, 90))
            close_date = rand_date(30, 200)

            # Pick assignees based on status
            assigned_sh  = random.choice(sh_list).user_id if sh_list else None
            assigned_sa  = random.choice(sa_list).user_id if wf_status not in (
                "NEW_FROM_CRM",) and sa_list else None
            assigned_ph  = random.choice(ph_list).user_id if wf_status in (
                "WAITING_PH_APPROVAL", "READY_FOR_MGMT_REVIEW",
                "APPROVED", "REJECTED") and ph_list else None

            # Approval statuses
            gh_approval = "APPROVED" if wf_status in ("APPROVED",) else (
                "REJECTED" if wf_status == "REJECTED" else "PENDING"
            )
            ph_approval = "APPROVED" if wf_status in (
                "READY_FOR_MGMT_REVIEW", "APPROVED") else (
                "REJECTED" if wf_status == "REJECTED" else "PENDING"
            )
            sh_approval = "APPROVED" if wf_status in (
                "READY_FOR_MGMT_REVIEW", "APPROVED") else "PENDING"

            opp = Opportunity(
                opp_id               = f"SEED-{1000+i}",
                opp_number           = f"BQS-{2024100+i}",
                opp_name             = f"{customer} {practice_n} Initiative",
                customer_name        = customer,
                geo                  = geo,
                currency             = "USD",
                deal_value           = deal_value,
                stage                = stage,
                close_date           = close_date,
                crm_last_updated_at  = crm_ts,
                local_last_synced_at = now(),
                workflow_status      = wf_status,
                is_active            = True,
                primary_practice_id  = practice_id,
                assigned_sales_head_id = assigned_sh,
                assigned_sa_id       = assigned_sa,
                assigned_practice_head_id = assigned_ph,
                gh_approval_status   = gh_approval,
                ph_approval_status   = ph_approval,
                sh_approval_status   = sh_approval,
                combined_submission_ready = wf_status in (
                    "READY_FOR_MGMT_REVIEW", "APPROVED", "REJECTED"),
            )
            db.add(opp)
            inserted += 1

        db.commit()
        print(f"\n  ✅  Inserted {inserted} opportunities successfully!")

        # ---- 4. Add a few score versions for UNDER_ASSESSMENT / WAITING_PH ----
        sections = db.query(OppScoreSection).all()
        if sections:
            scorable_opps = (
                db.query(Opportunity)
                .filter(Opportunity.workflow_status.in_([
                    "UNDER_ASSESSMENT", "WAITING_PH_APPROVAL",
                    "READY_FOR_MGMT_REVIEW", "APPROVED", "REJECTED"
                ]))
                .limit(15)
                .all()
            )
            print(f"\n  Adding score versions for {len(scorable_opps)} opportunities...")
            for opp in scorable_opps:
                existing_ver = db.query(OppScoreVersion).filter(
                    OppScoreVersion.opp_id == opp.opp_id
                ).first()
                if existing_ver:
                    continue
                sa_uid = opp.assigned_sa_id or (sa_list[0].user_id if sa_list else None)
                ver = OppScoreVersion(
                    score_version_id = str(uuid.uuid4()),
                    opp_id           = opp.opp_id,
                    version_no       = 1,
                    status           = "SUBMITTED" if opp.workflow_status in (
                        "WAITING_PH_APPROVAL", "READY_FOR_MGMT_REVIEW",
                        "APPROVED", "REJECTED") else "DRAFT",
                    overall_score    = random.randint(55, 95),
                    confidence_level = random.choice(["High", "Medium", "Low"]),
                    recommendation   = random.choice(["BID", "NO_BID", "CONDITIONAL"]),
                    summary_comment  = "Strong opportunity aligned with our portfolio.",
                    created_by_user_id = sa_uid,
                    sa_submitted     = True,
                    sp_submitted     = True,
                    created_at       = now() - timedelta(days=random.randint(1, 30)),
                    submitted_at     = now() - timedelta(days=random.randint(1, 15)),
                )
                db.add(ver)
                db.flush()

                # Section values
                for section in sections:
                    sv = OppScoreSectionValue(
                        score_value_id   = str(uuid.uuid4()),
                        score_version_id = ver.score_version_id,
                        section_code     = section.section_code,
                        score            = round(random.uniform(2, 5), 1),
                        notes            = "Assessment notes for this section.",
                        selected_reasons = [],
                    )
                    db.add(sv)

            db.commit()
            print("  ✅  Score versions created.")

        # ---- 5. Summary -------------------------------------------------------
        total = db.query(Opportunity).count()
        print(f"\n{'='*65}")
        print(f"  TOTAL OPPORTUNITIES IN DATABASE: {total}")
        print(f"  Status breakdown:")
        from sqlalchemy import func
        rows = (
            db.query(Opportunity.workflow_status, func.count(Opportunity.opp_id))
            .group_by(Opportunity.workflow_status)
            .all()
        )
        for status, cnt in sorted(rows, key=lambda x: x[0] or ""):
            print(f"    {status or 'NULL':<30} : {cnt}")
        print(f"{'='*65}")
        print("\n🚀 Done! Refresh your browser to see data on all dashboards.")

    except Exception as exc:
        db.rollback()
        print(f"\n❌ Seeding failed: {exc}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_opportunities()
