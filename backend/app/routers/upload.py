
import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
import uuid
from backend.app.core.logging_config import get_logger

logger = get_logger("upload_router")

router = APIRouter(prefix="/api/upload", tags=["upload"])

# Define upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Generate a safe filename
        ext = os.path.splitext(file.filename)[1]
        safe_name = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(UPLOAD_DIR, safe_name)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"✅ File uploaded: {safe_name}")
        return {"filename": safe_name, "original_name": file.filename}
    except Exception as e:
        logger.error(f"❌ Upload Error: {e}")
        raise HTTPException(500, f"Upload failed: {str(e)}")

