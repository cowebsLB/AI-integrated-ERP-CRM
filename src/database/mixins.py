"""
Database mixins for automatic sync queue management.
"""
from typing import Optional
from sqlalchemy.orm import Session
from src.database.base import SessionLocal
from src.services.sync_service import SyncService

# Global sync service instance
_sync_service: Optional[SyncService] = None

def get_sync_service() -> SyncService:
    """Get or create sync service instance."""
    global _sync_service
    if _sync_service is None:
        _sync_service = SyncService()
    return _sync_service


class SyncableMixin:
    """
    Mixin class for models that should be synced with Supabase.
    Add this to your model classes to enable automatic sync queue management.
    """
    
    def to_dict(self) -> dict:
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def add_to_sync_queue(self, operation: str = "update"):
        """Add this record to the sync queue."""
        sync_service = get_sync_service()
        if sync_service.is_enabled():
            table_name = self.__table__.name
            record_id = str(getattr(self, 'id', ''))
            data = self.to_dict() if operation != "delete" else None
            sync_service.add_to_queue(table_name, record_id, operation, data)
    
    @classmethod
    def after_insert(cls, mapper, connection, target):
        """Hook called after insert."""
        target.add_to_sync_queue("create")
    
    @classmethod
    def after_update(cls, mapper, connection, target):
        """Hook called after update."""
        target.add_to_sync_queue("update")
    
    @classmethod
    def after_delete(cls, mapper, connection, target):
        """Hook called after delete."""
        target.add_to_sync_queue("delete")

