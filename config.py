"""
Configuration management for the ERP-CRM application.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
EXPORTS_DIR = BASE_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"
MODELS_DIR = BASE_DIR / "models"

# Create directories if they don't exist
for directory in [DATA_DIR, UPLOADS_DIR, EXPORTS_DIR, LOGS_DIR, MODELS_DIR]:
    directory.mkdir(exist_ok=True)

# Database configuration
# Local SQLite database (primary - for fast local operations)
LOCAL_DATABASE_URL = os.getenv("LOCAL_DATABASE_URL", f"sqlite:///{DATA_DIR}/erp_crm.db")

# Supabase configuration (cloud sync)
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_ENABLED = os.getenv("SUPABASE_ENABLED", "false").lower() == "true"

# Sync configuration
SYNC_ENABLED = SUPABASE_ENABLED
SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", "300"))  # seconds (default: 5 minutes)
SYNC_ON_STARTUP = os.getenv("SYNC_ON_STARTUP", "true").lower() == "true"
SYNC_AUTO = os.getenv("SYNC_AUTO", "true").lower() == "true"  # Auto-sync on changes

# Legacy support (for backward compatibility)
DATABASE_URL = LOCAL_DATABASE_URL

# AI/LLM configuration
# Option 1: Ollama (recommended - 638MB, faster)
USE_OLLAMA = os.getenv("USE_OLLAMA", "true").lower() == "true"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "tinyllama")

# Option 2: Hugging Face (alternative)
TINYLLAMA_PATH = os.getenv("TINYLLAMA_PATH", "")  # Set path to your TinyLlama folder
TINYLLAMA_MODEL_NAME = os.getenv("TINYLLAMA_MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")

# Application settings
APP_NAME = "AI-Integrated ERP-CRM"
APP_VERSION = "1.0.0"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

# Update checker configuration
GITHUB_REPO_OWNER = os.getenv("GITHUB_REPO_OWNER", "cowebsLB")
GITHUB_REPO_NAME = os.getenv("GITHUB_REPO_NAME", "AI-integrated-ERP-CRM")
CHECK_UPDATES_ON_STARTUP = os.getenv("CHECK_UPDATES_ON_STARTUP", "true").lower() == "true"
AUTO_CHECK_UPDATES = os.getenv("AUTO_CHECK_UPDATES", "true").lower() == "true"

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
BCRYPT_ROUNDS = 12

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "app.log"

# AI Settings
AI_MAX_TOKENS = 512
AI_TEMPERATURE = 0.7
AI_TOP_P = 0.9

