from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from typing import List, Optional
import uvicorn
import os
from dotenv import load_dotenv

# Ensure init_db is imported
from database import init_db, get_db, Opportunity, Assessment

# Load environment variables from .env file if it exists (useful for local dev)
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs init_db immediately on startup
    init_db()
    yield

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
    Updates the sales_owner field with the primary SA name.
    """
    opp = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    # Update the sales_owner with the primary SA
    opp.sales_owner = assignment_data.get("primarySA", "")
    
    # You can also store additional metadata if needed
    # For now, we're just updating the sales_owner field
    
    db.commit()
    db.refresh(opp)
    
    return {
        "message": "Solution Architect assigned successfully",
        "opportunity_id": id,
        "assigned_to": opp.sales_owner
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

if __name__ == "__main__":
    # Local development entry point
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
