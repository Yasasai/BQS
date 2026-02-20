
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
import sys

# FIX: Add project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.database import init_db
from backend.sync_manager import sync_opportunities
from backend.app.routers import auth, inbox, scoring, opportunities, users

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 BQS Starting...")
    init_db()
    # Auto-Sync on Startup (Lightweight)
    try:
        from backend.sync_manager import sync_opportunities_async
        await sync_opportunities_async()
    except Exception as e:
        print(f"Startup Sync Error: {e}")
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

@app.post("/api/sync-force")
async def force_sync(background_tasks: BackgroundTasks):
    from backend.sync_manager import sync_opportunities_async
    background_tasks.add_task(sync_opportunities_async)
    return {"status": "started"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
