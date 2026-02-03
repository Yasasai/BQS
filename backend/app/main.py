
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
import sys

# Ensure backend module can be found ensuring we are in root
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.core.database import init_db
from backend.app.routers import auth, inbox, scoring, opportunities, users

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 BQS Starting...")
    init_db()
    # Auto-Sync on Startup (Disabled for faster startup)
    # Uncomment to enable auto-sync: sync_opportunities()
    # try:
    #     sync_opportunities()
    # except Exception as e:
    #     print(f"Startup Sync Error: {e}")
    print("✅ BQS Ready!")
    yield

app = FastAPI(title="BQS MVP", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(inbox.router)
app.include_router(scoring.router)
app.include_router(opportunities.router)


app.include_router(users.router)

from backend.app.services.async_sync import run_async_sync

@app.post("/api/sync")
async def trigger_sync(background_tasks: BackgroundTasks):
    """
    Trigger the high-performance async batch sync in the background.
    """
    background_tasks.add_task(run_async_sync)
    return {"message": "Async sync started in background"}



if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
