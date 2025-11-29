"""
Sync manager for automatic background synchronization.
"""
import logging
import threading
import time
from datetime import datetime
from typing import Optional
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from src.services.sync_service import SyncService
import config

logger = logging.getLogger(__name__)


class SyncManager(QObject):
    """Manages automatic background synchronization."""
    
    sync_status_changed = pyqtSignal(dict)  # Emits sync status updates
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sync_service = SyncService()
        self.timer: Optional[QTimer] = None
        self.is_syncing = False
        self._setup_auto_sync()
    
    def _setup_auto_sync(self):
        """Setup automatic sync timer if enabled."""
        if config.SYNC_AUTO and self.sync_service.is_enabled():
            self.timer = QTimer()
            self.timer.timeout.connect(self.sync)
            self.timer.start(config.SYNC_INTERVAL * 1000)  # Convert to milliseconds
            logger.info(f"Auto-sync enabled (interval: {config.SYNC_INTERVAL}s)")
    
    def sync(self, force: bool = False):
        """
        Perform synchronization (push pending changes).
        
        Args:
            force: Force sync even if one is in progress
        """
        if not self.sync_service.is_enabled():
            return
        
        if self.is_syncing and not force:
            logger.debug("Sync already in progress, skipping")
            return
        
        self.is_syncing = True
        logger.info("Starting sync...")
        
        try:
            # Push pending changes
            stats = self.sync_service.push_pending_changes()
            
            # Emit status update
            status = self.sync_service.get_queue_status()
            status.update(stats)
            self.sync_status_changed.emit(status)
            
            logger.info(f"Sync completed: {stats}")
            
        except Exception as e:
            logger.error(f"Error during sync: {e}")
        finally:
            self.is_syncing = False
    
    def sync_now(self):
        """Trigger immediate sync."""
        self.sync(force=True)
    
    def get_status(self) -> dict:
        """Get current sync status."""
        if not self.sync_service.is_enabled():
            return {"enabled": False}
        
        status = self.sync_service.get_queue_status()
        status["enabled"] = True
        status["is_syncing"] = self.is_syncing
        return status
    
    def start(self):
        """Start the sync manager."""
        if config.SYNC_ON_STARTUP:
            # Delay initial sync to let app initialize
            QTimer.singleShot(5000, self.sync_now)
            logger.info("Sync manager started (startup sync scheduled)")
    
    def stop(self):
        """Stop the sync manager."""
        if self.timer:
            self.timer.stop()
        logger.info("Sync manager stopped")

