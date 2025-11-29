"""
Main entry point for the AI-Integrated ERP-CRM application.
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.gui.main_window import MainWindow
from src.utils.logger import setup_logger
from src.database.base import init_db
from src.services.sync_manager import SyncManager
import config

def main():
    """Initialize and run the application."""
    # Setup logging
    logger = setup_logger()
    logger.info(f"Starting {config.APP_NAME} v{config.APP_VERSION}")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.setApplicationVersion(config.APP_VERSION)
    
    # Set application style (optional)
    app.setStyle("Fusion")
    
    # Initialize sync manager
    sync_manager = SyncManager()
    sync_manager.start()
    
    # Create and show main window
    window = MainWindow()
    window.set_sync_manager(sync_manager)  # Pass sync manager to window
    window.show()
    
    logger.info("Application started successfully")
    
    # Run event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

