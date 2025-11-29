"""
Database connection and session management.
Supports local SQLite database with optional Supabase sync.
"""
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
import config

logger = logging.getLogger(__name__)

# Create base class for models
Base = declarative_base()

# Create engine for local SQLite database
engine = create_engine(
    config.LOCAL_DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    connect_args={"check_same_thread": False} if "sqlite" in config.LOCAL_DATABASE_URL else {}
)

# Enable foreign keys for SQLite
if "sqlite" in config.LOCAL_DATABASE_URL:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables."""
    # Import all models to ensure they're registered
    from src.database.models import erp_models, crm_models
    
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")

