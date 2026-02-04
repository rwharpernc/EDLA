"""
Configuration file for Elite Dangerous Log Analyzer
"""
import os
import sys
from pathlib import Path

# Application metadata
APP_NAME = "EDLA"
APP_VERSION = "Alpha 1.03"
APP_AUTHOR = "R.W. Harper"
APP_DESCRIPTION = "Elite Dangerous Log Analyzer"

# Determine if running as frozen executable (PyInstaller)
def is_frozen():
    """Check if application is running as a compiled executable"""
    return getattr(sys, 'frozen', False)

# Get base directory - works for both development and frozen executable
def get_base_dir():
    """Get the base directory of the application"""
    if is_frozen():
        # Running as compiled executable
        return Path(sys.executable).parent
    else:
        # Running as script
        return Path(__file__).parent

BASE_DIR = get_base_dir()

# Assets directory (for icons, images, etc.)
ASSETS_DIR = BASE_DIR / "assets"

# Documents directory
DOCUMENTS_DIR = BASE_DIR / "documents"

# Default Elite Dangerous log directory
DEFAULT_LOG_DIR = Path(os.path.expanduser("~")) / "Saved Games" / "Frontier Developments" / "Elite Dangerous"

# Application data directory (for profiles, session DB, etc.)
APP_DATA_DIR = Path(os.path.expanduser("~")) / ".edla"
PROFILES_DIR = APP_DATA_DIR / "profiles"
# SQLite database for sessions and processed file tracking
EDLA_DB_PATH = APP_DATA_DIR / "edla.db"

# Application logs directory (in same directory as application)
LOGS_DIR = BASE_DIR / "logs"

# Log revalidation timeout (ms) – if exceeded, revalidation is cancelled and user is notified
REVALIDATE_TIMEOUT_MS = 120_000  # 2 minutes

# Ensure directories exist
APP_DATA_DIR.mkdir(exist_ok=True)
PROFILES_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

