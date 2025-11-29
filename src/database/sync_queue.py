"""
Sync queue models for tracking changes to be synced with Supabase.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from src.database.base import Base


class SyncQueue(Base):
    """
    Queue table for tracking changes that need to be synced with Supabase.
    """
    __tablename__ = "sync_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(100), nullable=False, index=True)  # e.g., 'contacts', 'invoices'
    record_id = Column(String(100), nullable=False, index=True)  # ID of the record
    operation = Column(String(20), nullable=False)  # 'create', 'update', 'delete'
    data = Column(JSON, nullable=True)  # Full record data (for create/update)
    status = Column(String(20), default="pending", index=True)  # 'pending', 'syncing', 'synced', 'failed'
    retry_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    synced_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<SyncQueue(id={self.id}, table={self.table_name}, operation={self.operation}, status={self.status})>"


class SyncMetadata(Base):
    """
    Metadata table for tracking sync state and last sync times.
    """
    __tablename__ = "sync_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(100), unique=True, nullable=False, index=True)
    last_sync_at = Column(DateTime, nullable=True)  # Last successful sync time
    last_pull_at = Column(DateTime, nullable=True)  # Last successful pull time
    last_push_at = Column(DateTime, nullable=True)  # Last successful push time
    sync_enabled = Column(Boolean, default=True)
    conflict_resolution = Column(String(20), default="local")  # 'local', 'remote', 'merge'
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SyncMetadata(table={self.table_name}, last_sync={self.last_sync_at})>"

