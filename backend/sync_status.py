"""
Sync Status Tracking Module
Provides API endpoints and utilities to track sync status
"""
from datetime import datetime
from typing import Optional, Dict
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean
from database import Base, SessionLocal


class SyncLog(Base):
    """Track each sync operation"""
    __tablename__ = "sync_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    sync_type = Column(String)  # FULL or INCREMENTAL
    status = Column(String)  # RUNNING, SUCCESS, FAILED
    
    total_fetched = Column(Integer, default=0)
    new_records = Column(Integer, default=0)
    updated_records = Column(Integer, default=0)
    failed_records = Column(Integer, default=0)
    
    error_message = Column(String, nullable=True)
    sync_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' (reserved word)
    
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)


def get_last_sync_status() -> Optional[Dict]:
    """Get the status of the most recent sync"""
    db = SessionLocal()
    try:
        last_sync = db.query(SyncLog).order_by(SyncLog.started_at.desc()).first()
        
        if not last_sync:
            return None
        
        return {
            'id': last_sync.id,
            'sync_type': last_sync.sync_type,
            'status': last_sync.status,
            'total_fetched': last_sync.total_fetched,
            'new_records': last_sync.new_records,
            'updated_records': last_sync.updated_records,
            'failed_records': last_sync.failed_records,
            'started_at': last_sync.started_at.isoformat() if last_sync.started_at else None,
            'completed_at': last_sync.completed_at.isoformat() if last_sync.completed_at else None,
            'duration_seconds': last_sync.duration_seconds,
            'error_message': last_sync.error_message
        }
    finally:
        db.close()


def create_sync_log(sync_type: str) -> int:
    """Create a new sync log entry and return its ID"""
    db = SessionLocal()
    try:
        log = SyncLog(
            sync_type=sync_type,
            status='RUNNING',
            started_at=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log.id
    finally:
        db.close()


def update_sync_log(log_id: int, stats: Dict, status: str = 'SUCCESS', error: str = None):
    """Update sync log with completion stats"""
    db = SessionLocal()
    try:
        log = db.query(SyncLog).filter(SyncLog.id == log_id).first()
        if log:
            log.status = status
            log.total_fetched = stats.get('total_fetched', 0)
            log.new_records = stats.get('new_records', 0)
            log.updated_records = stats.get('updated_records', 0)
            log.failed_records = stats.get('failed_records', 0)
            log.completed_at = datetime.utcnow()
            log.error_message = error
            
            if log.started_at:
                duration = (log.completed_at - log.started_at).total_seconds()
                log.duration_seconds = int(duration)
            
            db.commit()
    finally:
        db.close()


def get_sync_history(limit: int = 10):
    """Get recent sync history"""
    db = SessionLocal()
    try:
        logs = db.query(SyncLog).order_by(SyncLog.started_at.desc()).limit(limit).all()
        
        return [{
            'id': log.id,
            'sync_type': log.sync_type,
            'status': log.status,
            'total_fetched': log.total_fetched,
            'new_records': log.new_records,
            'updated_records': log.updated_records,
            'failed_records': log.failed_records,
            'started_at': log.started_at.isoformat() if log.started_at else None,
            'completed_at': log.completed_at.isoformat() if log.completed_at else None,
            'duration_seconds': log.duration_seconds
        } for log in logs]
    finally:
        db.close()
