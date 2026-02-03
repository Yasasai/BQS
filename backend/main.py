
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
import sys

# FIX: Add project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.database import init_db
from backend.app.services.async_sync import run_async_sync
from backend.app.routers import auth, inbox, scoring, upload, opportunities, users

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 BQS Starting...")
    init_db()
    # NEW: Run High-Performance Async Sync on Startup
    print("🚀 Triggering Async Batch Sync...")
    import asyncio
    asyncio.create_task(run_async_sync())
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
app.include_router(upload.router)
app.include_router(opportunities.router)
# app.include_router(users.router) # If users router exists in app/routers

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Prevent 404 errors when accessing API via browser"""
    from fastapi.responses import Response
    return Response(status_code=204)  # No Content

@app.post("/api/sync")
async def trigger_sync(background_tasks: BackgroundTasks):
    """
    Trigger the high-performance async batch sync in the background.
    """
    background_tasks.add_task(run_async_sync)
    return {"message": "Async sync started in background"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
