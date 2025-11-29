"""
Sync service for synchronizing data between local SQLite and Supabase.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

import config
from src.database.base import SessionLocal
from src.database.sync_queue import SyncQueue, SyncMetadata

logger = logging.getLogger(__name__)


class SyncService:
    """Service for syncing data between local SQLite and Supabase."""
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.enabled = config.SYNC_ENABLED and SUPABASE_AVAILABLE
        
        if self.enabled and config.SUPABASE_URL and config.SUPABASE_KEY:
            try:
                self.supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self.enabled = False
        else:
            logger.info("Supabase sync is disabled or not configured")
    
    def is_enabled(self) -> bool:
        """Check if sync is enabled and available."""
        return self.enabled and self.supabase is not None
    
    def add_to_queue(
        self,
        table_name: str,
        record_id: str,
        operation: str,
        data: Optional[Dict[str, Any]] = None
    ) -> SyncQueue:
        """
        Add a change to the sync queue.
        
        Args:
            table_name: Name of the table
            record_id: ID of the record
            operation: 'create', 'update', or 'delete'
            data: Record data (for create/update operations)
            
        Returns:
            Created SyncQueue entry
        """
        if not self.is_enabled():
            logger.debug("Sync disabled, skipping queue addition")
            return None
        
        db = SessionLocal()
        try:
            queue_item = SyncQueue(
                table_name=table_name,
                record_id=str(record_id),
                operation=operation,
                data=data,
                status="pending"
            )
            db.add(queue_item)
            db.commit()
            db.refresh(queue_item)
            logger.debug(f"Added to sync queue: {table_name}.{record_id} ({operation})")
            return queue_item
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding to sync queue: {e}")
            raise
        finally:
            db.close()
    
    def push_pending_changes(self, limit: int = 100) -> Dict[str, int]:
        """
        Push pending changes from queue to Supabase.
        
        Args:
            limit: Maximum number of items to process in one batch
            
        Returns:
            Dictionary with sync statistics
        """
        if not self.is_enabled():
            return {"pushed": 0, "failed": 0, "skipped": 0}
        
        stats = {"pushed": 0, "failed": 0, "skipped": 0}
        db = SessionLocal()
        
        try:
            # Get pending items
            pending_items = db.query(SyncQueue).filter(
                SyncQueue.status == "pending"
            ).limit(limit).all()
            
            for item in pending_items:
                try:
                    # Mark as syncing
                    item.status = "syncing"
                    db.commit()
                    
                    # Push to Supabase
                    success = self._push_item(item)
                    
                    if success:
                        item.status = "synced"
                        item.synced_at = datetime.utcnow()
                        stats["pushed"] += 1
                        logger.info(f"Synced {item.table_name}.{item.record_id} ({item.operation})")
                    else:
                        item.status = "failed"
                        item.retry_count += 1
                        stats["failed"] += 1
                        logger.warning(f"Failed to sync {item.table_name}.{item.record_id}")
                    
                    db.commit()
                    
                except Exception as e:
                    db.rollback()
                    item.status = "failed"
                    item.retry_count += 1
                    item.error_message = str(e)
                    stats["failed"] += 1
                    logger.error(f"Error syncing {item.table_name}.{item.record_id}: {e}")
                    db.commit()
            
            return stats
            
        except Exception as e:
            logger.error(f"Error in push_pending_changes: {e}")
            return stats
        finally:
            db.close()
    
    def _push_item(self, item: SyncQueue) -> bool:
        """Push a single item to Supabase."""
        try:
            table = self.supabase.table(item.table_name)
            
            if item.operation == "create":
                result = table.insert(item.data).execute()
                return len(result.data) > 0
                
            elif item.operation == "update":
                result = table.update(item.data).eq("id", item.record_id).execute()
                return len(result.data) > 0
                
            elif item.operation == "delete":
                result = table.delete().eq("id", item.record_id).execute()
                return True  # Delete always succeeds if record exists or not
                
            return False
            
        except Exception as e:
            logger.error(f"Error pushing item to Supabase: {e}")
            return False
    
    def pull_from_supabase(self, table_name: str, last_sync: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Pull changes from Supabase to local database.
        
        Args:
            table_name: Name of the table to pull
            last_sync: Only pull records updated after this time
            
        Returns:
            List of records pulled from Supabase
        """
        if not self.is_enabled():
            return []
        
        try:
            table = self.supabase.table(table_name)
            
            # Build query
            query = table.select("*")
            if last_sync:
                # Assuming Supabase has updated_at column
                query = query.gte("updated_at", last_sync.isoformat())
            
            result = query.execute()
            logger.info(f"Pulled {len(result.data)} records from {table_name}")
            return result.data
            
        except Exception as e:
            logger.error(f"Error pulling from Supabase {table_name}: {e}")
            return []
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current sync queue status."""
        db = SessionLocal()
        try:
            pending = db.query(SyncQueue).filter(SyncQueue.status == "pending").count()
            syncing = db.query(SyncQueue).filter(SyncQueue.status == "syncing").count()
            failed = db.query(SyncQueue).filter(SyncQueue.status == "failed").count()
            synced = db.query(SyncQueue).filter(SyncQueue.status == "synced").count()
            
            return {
                "pending": pending,
                "syncing": syncing,
                "failed": failed,
                "synced": synced,
                "total": pending + syncing + failed + synced
            }
        finally:
            db.close()
    
    def clear_synced_items(self, older_than_days: int = 7):
        """Clear old synced items from the queue."""
        db = SessionLocal()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
            deleted = db.query(SyncQueue).filter(
                and_(
                    SyncQueue.status == "synced",
                    SyncQueue.synced_at < cutoff_date
                )
            ).delete()
            db.commit()
            logger.info(f"Cleared {deleted} old synced items")
            return deleted
        except Exception as e:
            db.rollback()
            logger.error(f"Error clearing synced items: {e}")
            return 0
        finally:
            db.close()

