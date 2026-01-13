from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from typing import List, Optional
import uvicorn
import os
from dotenv import load_dotenv


# Fix for ModuleNotFoundError when running from root
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Ensure init_db is imported
from database import init_db, get_db, Opportunity, Assessment, SessionLocal
from sync_manager import sync_opportunities


# Load environment variables from .env file with absolute path for reliability
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path=env_path)

# ----------------------------------------------------------------
# PRIORITY SYNC LIST (User Defined)
# ----------------------------------------------------------------
PRIORITY_IDS = [
    '1602736', '1602737', '1602738', '1693827', 
    '1658743', '1658758', '1657755', '1744044', 
    '1754130', '17592771', '1755209', '1733846'
]

def fetch_priority_ids():
    """
    Startup Task: Fetch specific Priority IDs regardless of sync schedule.
    """
    print("\n[Startup] 🚀 Fetching Priority Opportunity IDs...")
    from oracle_service import map_oracle_to_db, get_auth_header
    import httpx
    import time
    
    auth_header = get_auth_header()
    if not auth_header:
        print("⚠️ [Startup] No Oracle Credentials found. Skipping priority fetch.")
        return

    db = SessionLocal()
    base_url = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")
    search_url = f"{base_url}/crmRestApi/resources/latest/opportunities"
    
    with httpx.Client(headers=auth_header, timeout=30.0) as client:
        for opty_number in PRIORITY_IDS:
            try:
                # Search Query
                query = f"RecordSet='ALL';OptyNumber='{opty_number}'"
                response = client.get(search_url, params={'q': query, 'onlyData': 'true', 'limit': '1'})
                
                if response.status_code == 200:
                    items = response.json().get('items', [])
                    if items:
                        record = items[0]
                        print(f"   ✅ Found: {opty_number} ({record.get('Name')[:20]}...)")
                        
                        mapped = map_oracle_to_db(record)
                        if mapped:
                            primary_data = mapped["primary"]
                            details_data = mapped["details"]
                            
                            # Upsert Primary
                            existing = db.query(Opportunity).filter(Opportunity.remote_id == str(opty_number)).first()
                            if existing:
                                for k, v in primary_data.items(): setattr(existing, k, v)
                            else:
                                db.add(Opportunity(**primary_data, workflow_status='NEW_FROM_CRM'))
                                
                            # Upsert Details
                            existing_details = db.query(OpportunityDetails).filter(OpportunityDetails.opty_number == str(opty_number)).first()
                            if existing_details:
                                for k, v in details_data.items(): setattr(existing_details, k, v)
                            else:
                                db.add(OpportunityDetails(**details_data))
                                
                            db.commit()
                    else:
                        print(f"   ⚠️  Not Found: {opty_number}")
                else:
                    print(f"   ❌ Error {response.status_code}: {opty_number}")
                    
                time.sleep(0.2) # Polite pause
                
            except Exception as e:
                print(f"   ❌ Exception {opty_number}: {e}")
                db.rollback()
    
    db.close()
    print("[Startup] Priority Fetch Complete.\n")

# Scheduler
try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    scheduler = AsyncIOScheduler()
    HAS_SCHEDULER = True
except ImportError:
    print("Warning: APScheduler not found. Automated sync (cronjob) will not run.")
    HAS_SCHEDULER = False
    scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs init_db immediately on startup
    print("\n" + "="*60)
    print("🚀 BQS Backend Starting...")
    print("="*60)
    
    print("\n[1/2] Initializing database...")
    init_db()
    print("✓ Database initialized")
    
    print("\n[2/4] Running self-healing migrations...")
    try:
        from sqlalchemy import inspect, text
        from database import engine, Base
        
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        db = SessionLocal()
        try:
            for table_name, table in Base.metadata.tables.items():
                if table_name in existing_tables:
                    db_columns = {col['name'] for col in inspector.get_columns(table_name)}
                    model_columns = {col.name for col in table.columns}
                    missing = model_columns - db_columns
                    
                    if missing:
                        print(f"🔧 Healing table '{table_name}' (missing: {missing})")
                        for col_name in missing:
                            col = table.columns[col_name]
                            col_type = col.type.compile(dialect=engine.dialect)
                            nullable = "NULL" if col.nullable else "NOT NULL"
                            sql = f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {col_name} {col_type} {nullable}"
                            db.execute(text(sql))
                        db.commit()
            print("✓ Database schema is synchronized")
        except Exception as e:
            db.rollback()
            print(f"⚠️  Migration error: {e}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"⚠️  Self-healing check failed: {e}")

    # Priority Fetch on Startup
    print("\n[3/4] Running Priority ID Sync...")
    try:
        fetch_priority_ids()
    except Exception as e:
        print(f"⚠️  Priority sync skipped: {e}")
    
    # Start Scheduler
    if HAS_SCHEDULER:
        print("\n[4/4] Starting Automated Sync Scheduler...")
        
        # Add the job: Run every 5 minutes
        # We set next_run_time=datetime.now() to trigger it IMMEDIATELY on startup
        from datetime import datetime
        scheduler.add_job(
            sync_opportunities, 
            'interval',
            minutes=5,
            id='oracle_sync_job', 
            kwargs={'force': True}, # Force FULL sync on the very first start
            next_run_time=datetime.now(),
            replace_existing=True
        )
        scheduler.start()
        print("✓ Scheduler active: Syncing every 5 minutes (next run: NOW)")
    
    print("\n" + "="*60)
    print("✓ Backend Ready!")
    print("="*60 + "\n")
    
    yield
    
    if HAS_SCHEDULER:
        scheduler.shutdown()

# Updated Title
app = FastAPI(title="BQS Antigravity", lifespan=lifespan)

# CORS Configuration
origins = ["*"] # Simplified for demo, restrict in prod

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "BQS Backend is Running", "status": "active"}

# --- Basic Opportunity Routes (MVP) ---

@app.get("/api/opportunities")
def get_opportunities(db: Session = Depends(get_db)):
    return db.query(Opportunity).all()

@app.get("/api/oracle-opportunity/{id}")
def get_opportunity_detail(id: int, db: Session = Depends(get_db)):
    """
    On-Demand Live Fetch (Smart Fallback Logic)
    1. Check local database (Primary & Details)
    2. Validate completeness
    3. If incomplete -> Live fetch from Oracle
    4. Upsert fresh data into BOTH tables
    """
    from oracle_service import fetch_single_opportunity, map_oracle_to_db
    from database import OpportunityDetails
    
    opp = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    # Get extended details
    details = db.query(OpportunityDetails).filter(OpportunityDetails.opty_number == opp.remote_id).first()
    
    # Check if data is complete (Self-Healing trigger)
    is_incomplete = not opp.practice or opp.deal_value == 0 or not details
    
    if is_incomplete:
        print(f"🔍 Data for {opp.remote_id} is incomplete. Fetching live from Oracle...")
        live_data = fetch_single_opportunity(opp.remote_id)
        if live_data:
            mapped_result = map_oracle_to_db(live_data)
            if mapped_result:
                primary_mapped = mapped_result["primary"]
                details_mapped = mapped_result["details"]
                
                # Update Primary record
                for key, val in primary_mapped.items():
                    setattr(opp, key, val)
                
                # Update/Create Details record
                if not details:
                    details = OpportunityDetails(**details_mapped)
                    db.add(details)
                else:
                    for key, val in details_mapped.items():
                        setattr(details, key, val)
                        
                db.commit()
                db.refresh(opp)
                if details: db.refresh(details)
                print(f"✅ Enriched {opp.remote_id} with live Oracle data.")
    
    # Return unified response
    response_data = {**{c.name: getattr(opp, c.name) for c in opp.__table__.columns}}
    if details:
        detail_fields = {c.name: getattr(details, c.name) for c in details.__table__.columns if c.name not in response_data}
        response_data["extended_details"] = detail_fields
        
    return response_data

@app.post("/api/sync-database")
def trigger_sync_endpoint(background_tasks: BackgroundTasks, full_restore: bool = False):
    """
    Trigger the Oracle -> Postgres sync process in the background.
    Incremental by default, Full Restore if specified.
    """
    background_tasks.add_task(sync_opportunities, force=full_restore)
    return {
        "message": f"Sync process ({'Full' if full_restore else 'Incremental'}) started in background.",
        "mode": "FULL" if full_restore else "INCREMENTAL"
    }

@app.post("/api/v1/sync-crm")
def trigger_crm_sync_manual(background_tasks: BackgroundTasks):
    """
    Manually trigger the Oracle CRM -> PostgreSQL Sync process.
    """
    background_tasks.add_task(sync_opportunities, force=False)
    return {
        "status": "success", 
        "message": "Oracle CRM Sync triggered successfully. Data is being fetched and upserted in the background."
    }

@app.get("/api/v1/sync-logs")
def get_sync_logs(db: Session = Depends(get_db)):
    """
    Fetch the latest CRM sync logs for UI debugging.
    """
    from database import SyncLog
    logs = db.query(SyncLog).order_by(SyncLog.started_at.desc()).limit(10).all()
    return logs

@app.get("/api/sync-status")
def get_sync_status(db: Session = Depends(get_db)):
    """Get the status of the most recent sync operation"""
    from database import SyncLog
    status = db.query(SyncLog).order_by(SyncLog.started_at.desc()).first()
    if not status:
        return {"status": "NO_SYNC_DATA", "message": "No sync has been performed yet."}
    return status

@app.get("/api/sync-history")
def get_sync_history_endpoint(limit: int = 10, db: Session = Depends(get_db)):
    """Get recent sync history"""
    from database import SyncLog
    history = db.query(SyncLog).order_by(SyncLog.started_at.desc()).limit(limit).all()
    return {
        "history": history,
        "total": len(history)
    }


@app.post("/api/opportunities/{id}/assign")
def assign_solution_architect(id: int, assignment_data: dict, db: Session = Depends(get_db)):
    """
    Assign a Solution Architect to an opportunity.
    """
    opp = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    # Update the assigned_sa with the primary SA
    opp.assigned_sa = assignment_data.get("primarySA", "")
    opp.status = "Scoring Pending"
    opp.workflow_status = "ASSIGNED_TO_SA"
    
    db.commit()
    db.refresh(opp)
    
    return {
        "message": "Solution Architect assigned successfully",
        "opportunity_id": id,
        "assigned_to": opp.assigned_sa,
        "status": opp.status
    }

@app.post("/api/opportunities/{id}/assign-practice")
def assign_practice(id: int, data: dict, db: Session = Depends(get_db)):
    opp = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opp: raise HTTPException(404, "Not found")
    opp.practice = data.get("practice")
    opp.workflow_status = "ASSIGNED_TO_PRACTICE"
    db.commit()
    return {"status": "success", "new_status": opp.workflow_status}

@app.post("/api/opportunities/{id}/assign-sa")
@app.post("/api/opportunities/{id}/assign-architect")
def assign_architect(id: int, data: dict, db: Session = Depends(get_db)):
    opp = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opp: raise HTTPException(404, "Not found")
    # Handle both frontend naming conventions
    opp.sa_owner = data.get("sa_owner") or data.get("primary_sa")
    opp.workflow_status = "PENDING_ASSESSMENT"
    db.commit()
    return {"status": "success", "new_status": opp.workflow_status}

@app.post("/api/opportunities/{id}/start-assessment")
def start_assessment(id: int, data: dict, db: Session = Depends(get_db)):
    opp = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opp: raise HTTPException(404, "Not found")
    opp.workflow_status = "UNDER_ASSESSMENT"
    db.commit()
    return {"status": "success", "new_status": opp.workflow_status}

@app.post("/api/opportunities/{id}/submit-assessment")
def submit_assessment(id: int, data: dict, db: Session = Depends(get_db)):
    opp = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opp: raise HTTPException(404, "Not found")
    opp.win_probability = data.get("score")
    opp.sa_notes = data.get("notes")
    opp.workflow_status = "REVIEW_PENDING"
    db.commit()
    return {"status": "success", "new_status": opp.workflow_status}

@app.post("/api/opportunities/{id}/practice-review")
def practice_review(id: int, data: dict, db: Session = Depends(get_db)):
    opp = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opp: raise HTTPException(404, "Not found")
    decision = data.get("decision") # APPROVED | REJECTED
    opp.practice_head_recommendation = decision
    if decision == "APPROVED":
        opp.workflow_status = "PENDING_GOVERNANCE"
    else:
        opp.workflow_status = "PENDING_ASSESSMENT" # Back to SA
    db.commit()
    return {"status": "success", "new_status": opp.workflow_status}

@app.post("/api/opportunities/{id}/final-decision")
def final_governance_decision(id: int, data: dict, db: Session = Depends(get_db)):
    opp = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opp: raise HTTPException(404, "Not found")
    decision = data.get("decision") # GO | NO_GO
    comments = data.get("comments") or data.get("reason")
    
    opp.management_decision = decision
    opp.close_reason = comments
    
    if decision == "GO":
        opp.workflow_status = "COMPLETED_BID"
    else:
        opp.workflow_status = "COMPLETED_NO_BID"
        
    db.commit()
    return {"status": "success", "new_status": opp.workflow_status}

# --- NEW: Review & Approval Workflow Endpoints ---

@app.post("/api/opportunities/{id}/send-to-practice-head")
def send_to_practice_head(id: int, data: dict, db: Session = Depends(get_db)):
    """
    SA submits their completed score to the Practice Head for review.
    Status: ASSIGNED_TO_SA or DRAFT_SCORE -> WAITING_PH_APPROVAL
    """
    opp = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opp: 
        raise HTTPException(404, "Opportunity not found")
    
    # Update the score if provided
    if "score" in data:
        opp.win_probability = data.get("score")
    if "notes" in data:
        opp.sa_notes = data.get("notes")
    
    opp.workflow_status = "WAITING_PH_APPROVAL"
    db.commit()
    db.refresh(opp)
    
    return {
        "status": "success", 
        "message": "Score submitted to Practice Head for review",
        "new_status": opp.workflow_status
    }

@app.post("/api/opportunities/{id}/accept-score")
def accept_score(id: int, data: dict, db: Session = Depends(get_db)):
    """
    Practice Head accepts the SA's score and endorses the bid.
    Status: WAITING_PH_APPROVAL -> READY_FOR_MGMT_REVIEW
    """
    opp = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opp: 
        raise HTTPException(404, "Opportunity not found")
    
    # Store PH endorsement
    opp.practice_head_recommendation = "APPROVED"
    if "comments" in data:
        opp.practice_head_notes = data.get("comments")
    
    opp.workflow_status = "READY_FOR_MGMT_REVIEW"
    db.commit()
    db.refresh(opp)
    
    return {
        "status": "success",
        "message": "Score accepted and forwarded to Management",
        "new_status": opp.workflow_status
    }

@app.post("/api/opportunities/{id}/reject-score")
def reject_score(id: int, data: dict, db: Session = Depends(get_db)):
    """
    Practice Head rejects the score and sends it back to SA for rework.
    Status: WAITING_PH_APPROVAL -> ASSIGNED_TO_SA
    """
    opp = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opp: 
        raise HTTPException(404, "Opportunity not found")
    
    # Store rejection reason
    opp.practice_head_recommendation = "REJECTED"
    if "reason" in data:
        opp.practice_head_notes = data.get("reason")
    
    opp.workflow_status = "ASSIGNED_TO_SA"
    db.commit()
    db.refresh(opp)
    
    return {
        "status": "success",
        "message": "Score rejected and returned to SA for rework",
        "new_status": opp.workflow_status
    }

if __name__ == "__main__":
    # Local development entry point
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
