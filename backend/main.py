
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
import sys
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure the backend root is in the path so we can import 'backend.app...'
# This allows running from within the backend directory OR from the project root.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from backend.app.core.database import init_db
from backend.app.routers import auth, inbox, scoring, opportunities, users, upload, batch_sync
from backend.app.core.logging_config import setup_logging, get_logger, correlation_id_ctx

# Initialize standardized logging
setup_logging()
logger = get_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 BQS Starting...")
    # Initialize DB (includes self-healing check for missing columns like pat_margin)
    try:
        init_db()
    except Exception as e:
        logger.error(f"Database Initialization Error: {e}")

    # Initialize APScheduler for background jobs
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from backend.sync_manager import sync_opportunities_async
        
        # Store scheduler in app state to gracefully shut it down later
        app.state.scheduler = AsyncIOScheduler()
        
        # Add background job to run every 1 hour
        app.state.scheduler.add_job(
            sync_opportunities_async,
            'interval',
            hours=1,
            id='background_sync_job',
            replace_existing=True
        )
        app.state.scheduler.start()
        logger.info("✅ APScheduler initialized for background sync (every 1 hour)")
    except ImportError:
        logger.warning("APScheduler not found. Background sync will not run automatically.")
    except Exception as e:
        logger.error(f"Startup Sync Scheduler Error: {e}")
    
    yield
    
    # Teardown
    if hasattr(app.state, 'scheduler'):
        try:
            app.state.scheduler.shutdown()
            logger.info("🛑 APScheduler shut down successfully.")
        except Exception as e:
            pass

app = FastAPI(title="BQS MVP", lifespan=lifespan)

# Correlation ID Middleware
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    token = correlation_id_ctx.set(correlation_id)
    try:
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
    finally:
        correlation_id_ctx.reset(token)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth.router)
app.include_router(inbox.router)
app.include_router(scoring.router)
app.include_router(opportunities.router)
app.include_router(users.router)
app.include_router(upload.router)
app.include_router(batch_sync.router)

@app.post("/api/sync-force")
async def force_sync(background_tasks: BackgroundTasks):
    from backend.sync_manager import sync_opportunities_async
    background_tasks.add_task(sync_opportunities_async)
    return {"status": "started"}


# ─────────────────────────────────────────────────────────────────────────────
# DEV SEED ENDPOINT  (Phase 4.6 Hotfix)
# Populates practice + opportunity tables with 30 realistic records.
# No auth required — delete or gate this endpoint before production.
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/api/dev/seed", tags=["Dev"])
def dev_seed():
    """
    Phase 4.6 Hotfix: Seed 30 opportunities directly inside the live server.
    Idempotent — skips if ≥30 opportunities already exist.
    """
    import random
    from datetime import datetime, timedelta, timezone
    from backend.app.core.database import SessionLocal
    from backend.app.models import (
        Practice, Opportunity, OppScoreVersion,
        OppScoreSectionValue, OppScoreSection,
        AppUser, Role, UserRole
    )

    CUSTOMERS = [
        "JPMorgan Chase", "FedEx Logistics", "Coca-Cola Enterprises",
        "Tesla Energy", "Apple EMEA", "Google Cloud", "Amazon Web Services",
        "Netflix Studios", "Microsoft Azure", "Samsung Electronics",
        "HSBC Banking", "Siemens AG", "Oracle Corp", "SAP SE", "Accenture",
        "Deloitte Advisory", "Goldman Sachs", "UnitedHealth Group",
        "Pfizer Ltd", "Boeing",
    ]
    GEO_LIST  = ["APAC", "EMEA", "NAMER", "LATAM", "MEA"]
    STAGES    = ["1. Prospect", "2. Develop", "3. Qualify", "4. Commit", "5. Closed Won"]
    PRACTICE_DATA = [
        ("CLOUD", "Cloud & Infrastructure"),
        ("CYBER", "Cybersecurity"),
        ("DATA",  "Data & Analytics"),
        ("AI_ML", "AI & Machine Learning"),
        ("ERP",   "Enterprise ERP"),
        ("NET",   "Networking"),
        ("SOFT",  "Software Engineering"),
    ]
    WORKFLOW_STATUSES = [
        "NEW_FROM_CRM", "ASSIGNED_TO_SA", "UNDER_ASSESSMENT",
        "WAITING_PH_APPROVAL", "READY_FOR_MGMT_REVIEW", "APPROVED", "REJECTED",
    ]

    def utcnow():
        return datetime.now(timezone.utc)

    db = SessionLocal()
    inserted_opps = 0
    inserted_versions = 0
    created_practices = 0
    errors = []

    try:
        # Guard: skip if already seeded
        existing = db.query(Opportunity).count()
        if existing >= 30:
            db.close()
            return {
                "status": "skipped",
                "message": f"Already have {existing} opportunities. Nothing to seed.",
                "opportunity_count": existing,
            }

        # 1. Ensure practices exist
        practice_map: dict[str, str] = {}
        for code, name in PRACTICE_DATA:
            p = db.query(Practice).filter(Practice.practice_name == name).first()
            if not p:
                p = Practice(
                    practice_id  = str(uuid.uuid4()),
                    practice_code= code[:20],
                    practice_name= name,
                )
                db.add(p)
                db.flush()
                created_practices += 1
            practice_map[name] = p.practice_id
        db.commit()

        # 2. Fetch user IDs by role
        def users_for_role(role_code: str):
            role = db.query(Role).filter(Role.role_code == role_code).first()
            if not role:
                return []
            return (
                db.query(AppUser.user_id)
                .join(UserRole, AppUser.user_id == UserRole.user_id)
                .filter(UserRole.role_id == role.role_id, AppUser.is_active == True)
                .all()
            )

        sh_ids = [r[0] for r in users_for_role("SH")]
        sa_ids = [r[0] for r in users_for_role("SA")]
        ph_ids = [r[0] for r in users_for_role("PH")]

        # 3. Build 30 opportunities across all statuses
        status_pool = (WORKFLOW_STATUSES * 5)[:30]
        random.shuffle(status_pool)

        for i, wf_status in enumerate(status_pool):
            customer   = CUSTOMERS[i % len(CUSTOMERS)]
            geo        = random.choice(GEO_LIST)
            prac_name  = random.choice(PRACTICE_DATA)[1]
            prac_id    = practice_map.get(prac_name)
            stage      = random.choice(STAGES)
            deal_value = round(random.uniform(500_000, 15_000_000), 2)
            crm_ts     = utcnow() - timedelta(days=random.randint(1, 90))
            close_dt   = utcnow() + timedelta(days=random.randint(30, 200))

            sh_id = random.choice(sh_ids) if sh_ids else None
            sa_id = (random.choice(sa_ids)
                     if sa_ids and wf_status != "NEW_FROM_CRM" else None)
            ph_id = (random.choice(ph_ids)
                     if ph_ids and wf_status in (
                         "WAITING_PH_APPROVAL", "READY_FOR_MGMT_REVIEW",
                         "APPROVED", "REJECTED") else None)

            gh_ap = "APPROVED" if wf_status == "APPROVED" else (
                    "REJECTED" if wf_status == "REJECTED" else "PENDING")
            ph_ap = "APPROVED" if wf_status in (
                    "READY_FOR_MGMT_REVIEW", "APPROVED") else (
                    "REJECTED" if wf_status == "REJECTED" else "PENDING")
            sh_ap = ("APPROVED" if wf_status in ("READY_FOR_MGMT_REVIEW", "APPROVED")
                     else "PENDING")
            sub_ready = wf_status in ("READY_FOR_MGMT_REVIEW", "APPROVED", "REJECTED")

            # Check for existing opp with same ID (idempotent)
            opp_id = f"SEED-{1000 + i}"
            if db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first():
                continue

            opp = Opportunity(
                opp_id                    = opp_id,
                opp_number                = f"BQS-{2024100 + i}",
                opp_name                  = f"{customer} {prac_name} Initiative",
                customer_name             = customer,
                geo                       = geo,
                currency                  = "USD",
                deal_value                = deal_value,
                stage                     = stage,
                close_date                = close_dt,
                crm_last_updated_at       = crm_ts,
                local_last_synced_at      = utcnow(),
                workflow_status           = wf_status,
                is_active                 = True,
                primary_practice_id       = prac_id,
                assigned_sales_head_id    = sh_id,
                assigned_sa_id            = sa_id,
                assigned_practice_head_id = ph_id,
                gh_approval_status        = gh_ap,
                ph_approval_status        = ph_ap,
                sh_approval_status        = sh_ap,
                combined_submission_ready = sub_ready,
            )
            db.add(opp)
            inserted_opps += 1

        db.commit()

        # 4. Add score versions for scored statuses
        sections = db.query(OppScoreSection).all()
        if sections:
            scored_statuses = (
                "UNDER_ASSESSMENT", "WAITING_PH_APPROVAL",
                "READY_FOR_MGMT_REVIEW", "APPROVED", "REJECTED",
            )
            scorable = (
                db.query(Opportunity)
                .filter(Opportunity.workflow_status.in_(scored_statuses))
                .limit(20)
                .all()
            )
            for opp in scorable:
                if db.query(OppScoreVersion).filter(
                        OppScoreVersion.opp_id == opp.opp_id).first():
                    continue

                is_submitted = opp.workflow_status in (
                    "WAITING_PH_APPROVAL", "READY_FOR_MGMT_REVIEW",
                    "APPROVED", "REJECTED")
                sa_uid = opp.assigned_sa_id or (sa_ids[0] if sa_ids else None)
                ver = OppScoreVersion(
                    score_version_id   = str(uuid.uuid4()),
                    opp_id             = opp.opp_id,
                    version_no         = 1,
                    status             = "SUBMITTED" if is_submitted else "DRAFT",
                    overall_score      = random.randint(55, 95),
                    confidence_level   = random.choice(["High", "Medium", "Low"]),
                    recommendation     = random.choice(["BID", "NO_BID", "CONDITIONAL"]),
                    summary_comment    = "Strong opportunity aligned with our portfolio.",
                    created_by_user_id = sa_uid,
                    sa_submitted       = True,
                    sp_submitted       = True,
                    created_at         = utcnow() - timedelta(days=random.randint(5, 30)),
                    submitted_at       = (utcnow() - timedelta(days=random.randint(1, 5))
                                         if is_submitted else None),
                )
                db.add(ver)
                db.flush()
                inserted_versions += 1

                for sec in sections:
                    db.add(OppScoreSectionValue(
                        score_value_id   = str(uuid.uuid4()),
                        score_version_id = ver.score_version_id,
                        section_code     = sec.section_code,
                        score            = round(random.uniform(2.0, 5.0), 1),
                        notes            = "Auto-generated assessment note.",
                        selected_reasons = [],
                    ))

            db.commit()

        # 5. Final count
        total = db.query(Opportunity).count()
        from sqlalchemy import func as sqlfunc
        breakdown = (
            db.query(Opportunity.workflow_status, sqlfunc.count(Opportunity.opp_id))
            .group_by(Opportunity.workflow_status)
            .all()
        )

        return {
            "status"             : "success",
            "message"            : "Database seeded successfully",
            "inserted_opps"      : inserted_opps,
            "inserted_versions"  : inserted_versions,
            "created_practices"  : created_practices,
            "total_opportunities": total,
            "breakdown"          : {s: c for s, c in breakdown},
        }

    except Exception as exc:
        db.rollback()
        logger.error(f"Dev seed failed: {exc}")
        return {"status": "error", "message": str(exc)}
    finally:
        db.close()


if __name__ == "__main__":
    # When running as python main.py
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

