"""
Batch Sync Router - Integrated into FastAPI Backend
====================================================

This router provides endpoints for batch sync with offset tracking.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the batch sync module
from batch_sync_with_offset import (
    batch_sync_opportunities,
    get_sync_status,
    reset_sync,
    get_synced_count
)

router = APIRouter(prefix="/api/batch-sync", tags=["Batch Sync"])


# ============================================================================
# MODELS
# ============================================================================

class BatchSyncRequest(BaseModel):
    batch_size: int = 5
    sync_name: str = "oracle_opportunities"


class SyncStatusResponse(BaseModel):
    sync_name: str
    current_offset: int
    total_synced: int
    last_sync_at: Optional[str]
    is_complete: bool
    total_in_db: int


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/start")
async def start_batch_sync(
    request: BatchSyncRequest,
    background_tasks: BackgroundTasks
):
    """
    Start batch sync with offset tracking
    
    Args:
        batch_size: Number of records per batch (default: 5)
        sync_name: Name of sync job (default: "oracle_opportunities")
    
    Returns:
        Status message
    """
    try:
        # Run sync in background
        background_tasks.add_task(
            batch_sync_opportunities,
            batch_size=request.batch_size,
            sync_name=request.sync_name
        )
        
        return {
            "status": "started",
            "message": f"Batch sync started with batch_size={request.batch_size}",
            "batch_size": request.batch_size,
            "sync_name": request.sync_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start-sync")
async def start_batch_sync_sync(
    batch_size: int = 5,
    background_tasks: BackgroundTasks = None
):
    """
    Start batch sync (synchronous) - waits for completion
    
    Args:
        batch_size: Number of records per batch (default: 5)
    
    Returns:
        Sync results
    """
    try:
        total_synced = batch_sync_opportunities(batch_size=batch_size)
        
        return {
            "status": "complete",
            "message": "Batch sync completed successfully",
            "total_synced": total_synced,
            "batch_size": batch_size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_batch_sync_status(sync_name: str = "oracle_opportunities"):
    """
    Get current batch sync status
    
    Args:
        sync_name: Name of sync job (default: "oracle_opportunities")
    
    Returns:
        Sync status details
    """
    try:
        status = get_sync_status(sync_name)
        count = get_synced_count()
        
        if not status:
            return {
                "status": "not_found",
                "message": f"No sync state found for '{sync_name}'",
                "total_in_db": count
            }
        
        return {
            "status": "success",
            "sync_name": status["sync_name"],
            "current_offset": status["current_offset"],
            "total_synced": status["total_synced"],
            "last_sync_at": str(status["last_sync_at"]) if status["last_sync_at"] else None,
            "is_complete": status["is_complete"],
            "total_in_db": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_batch_sync(sync_name: str = "oracle_opportunities"):
    """
    Reset batch sync to start from beginning
    
    Args:
        sync_name: Name of sync job (default: "oracle_opportunities")
    
    Returns:
        Status message
    """
    try:
        reset_sync(sync_name)
        
        return {
            "status": "success",
            "message": f"Sync state reset for '{sync_name}'",
            "sync_name": sync_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/count")
async def get_batch_sync_count():
    """
    Get count of synced opportunities in minimal_opportunities table
    
    Returns:
        Count of synced records
    """
    try:
        count = get_synced_count()
        
        return {
            "status": "success",
            "count": count,
            "table": "minimal_opportunities"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def batch_sync_health():
    """
    Health check for batch sync module
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "module": "batch_sync_with_offset",
        "endpoints": [
            "POST /api/batch-sync/start",
            "POST /api/batch-sync/start-sync",
            "GET /api/batch-sync/status",
            "POST /api/batch-sync/reset",
            "GET /api/batch-sync/count",
            "GET /api/batch-sync/health"
        ]
    }
