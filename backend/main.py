from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from typing import List, Optional
import uvicorn
import os
from dotenv import load_dotenv

# Ensure init_db is imported
from database import init_db, get_db, Opportunity, Assessment, SessionLocal
from sync_manager import sync_opportunities


# Load environment variables from .env file if it exists (useful for local dev)
load_dotenv()

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
    
    print("\n[2/2] Running self-healing migrations...")
    try:
        from sqlalchemy import inspect, text
        from database import engine, Opportunity
        
        # Check if opportunities table exists and has all required columns
        inspector = inspect(engine)
        if 'opportunities' in inspector.get_table_names():
            db_columns = {col['name'] for col in inspector.get_columns('opportunities')}
            model_columns = {col.name for col in Opportunity.__table__.columns}
            missing = model_columns - db_columns
            
            if missing:
                print(f"⚠️  Detected {len(missing)} missing columns: {missing}")
                print("🔧 Auto-healing database schema...")
                
                db = SessionLocal()
                try:
                    for col_name in missing:
                        col = Opportunity.__table__.columns[col_name]
                        col_type = col.type.compile(dialect=engine.dialect)
                        nullable = "NULL" if col.nullable else "NOT NULL"
                        
                        sql = f"ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS {col_name} {col_type} {nullable}"
                        print(f"  Adding: {col_name}")
                        db.execute(text(sql))
                        db.commit()
                    print("✓ Schema healed successfully")
                except Exception as e:
                    db.rollback()
                    print(f"⚠️  Warning: Could not auto-heal: {e}")
                finally:
                    db.close()
            else:
                print("✓ Schema is up to date")
        else:
            print("✓ Creating tables for the first time")
            
    except Exception as e:
        print(f"⚠️  Self-healing check failed: {e}")
    
    # Start Scheduler
    if HAS_SCHEDULER:
        print("\n[3/3] Starting Automated Sync Scheduler (Cronjob)...")
        # Process Fetching every 15 minutes
        scheduler.add_job(
            sync_opportunities, 
            'interval', 
            minutes=15, 
            id='oracle_sync_job', 
            replace_existing=True
        )
        scheduler.start()
        print("✓ Scheduler started: Syncing every 15 minutes.")
    
    print("\n" + "="*60)
    print("✓ Backend Ready!")
    print("="*60 + "\n")
    
    yield
    
    if HAS_SCHEDULER:
        scheduler.shutdown()

# Updated Title
app = FastAPI(title="BQS Antigravity", lifespan=lifespan)

# CORS Configuration
origins = [
    "http://localhost:5173", # Vite
    "http://localhost:3000", # React generic
 
]

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
    # In real app, would add pagination and filters.
    # For MVP, checking database usage.
    return db.query(Opportunity).all()

@app.get("/api/oracle-opportunity/{id}")
def get_opportunity_detail(id: int, db: Session = Depends(get_db)):
    opp = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opp

@app.post("/api/sync-database")
def trigger_sync(background_tasks: BackgroundTasks):
    """
    Trigger the Oracle -> Postgres sync process in the background.
    Does not block the request.
    """
    # Import inside function to avoid circular dependency issues if any,
    # though with current structure top-level import is fine too.
    from sync_manager import sync_opportunities
    
    # Running in background. sync_opportunities handles its own DB session.
    background_tasks.add_task(sync_opportunities)
    return {"message": "Sync process started in background."}

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
