

from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
import sys
import uuid

# Ensure backend module can be found ensuring we are in root
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.core.database import init_db
from backend.app.services.sync_manager import sync_opportunities
from backend.app.routers import auth, inbox, scoring, batch_sync, upload, opportunities
from backend.app.core.logging_config import setup_logging, get_logger, correlation_id_ctx

# Initialize standardized logging
setup_logging()
logger = get_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 BQS Starting...")
    init_db()
    # Auto-Sync on Startup (Lightweight)
    try:
        sync_opportunities()
    except Exception as e:
        logger.error(f"Startup Sync Error: {e}")
    yield

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
app.include_router(batch_sync.router)

@app.post("/api/sync-force")
def force_sync(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_opportunities)
    return {"status": "started"}

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)

