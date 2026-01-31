
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
from backend.app.routers import auth, inbox, scoring, upload

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 BQS Starting...")
    init_db()
    # Run sync in background on start using a thread
    import threading
    threading.Thread(target=sync_opportunities, daemon=True).start()
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
from backend.app.routers import opportunities, batch_sync
app.include_router(opportunities.router)
app.include_router(batch_sync.router)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Prevent 404 errors when accessing API via browser"""
    from fastapi.responses import Response
    return Response(status_code=204)  # No Content

@app.post("/api/sync-force")
def force_sync(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_opportunities)
    return {"status": "started"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
