"""
Configuration file for Elite Dangerous Log Analyzer.

Sensitive paths and keys are not hardcoded. Defaults use the current user's
home directory. Overrides are read from an external config file if present:
  - edla_config.json in the application base directory (next to the executable or main.py)

Do not commit edla_config.json to the repo. Use edla_config.sample.json as a template.
"""
import json
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
        return Path(sys.executable).parent
    return Path(__file__).parent

BASE_DIR = get_base_dir()

# Assets directory (for icons, images, etc.)
ASSETS_DIR = BASE_DIR / "assets"

# Documents directory
DOCUMENTS_DIR = BASE_DIR / "documents"

# Default paths (used when no external config or key not set)
_default_home = Path(os.path.expanduser("~"))
_default_log_dir = _default_home / "Saved Games" / "Frontier Developments" / "Elite Dangerous"
_default_app_data = _default_home / ".edla"

CONFIG_FILENAME = "edla_config.json"
SAMPLE_CONFIG_FILENAME = "edla_config.sample.json"


def _load_external_config():
    """Load optional external config from BASE_DIR. Returns dict or None."""
    config_path = BASE_DIR / CONFIG_FILENAME
    if not config_path.exists():
        return None
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _resolve_path(value):
    """Convert config value to absolute Path. Expands user and env vars."""
    if value is None or value == "":
        return None
    p = Path(os.path.expanduser(os.path.expandvars(str(value).strip())))
    return p.resolve() if p else None


def _apply_config():
    """Set DEFAULT_LOG_DIR, APP_DATA_DIR, EDLA_DB_PATH from defaults and optional external config."""
    log_dir = _default_log_dir
    app_data_dir = _default_app_data

    cfg = _load_external_config()
    if cfg:
        if "log_dir" in cfg:
            resolved = _resolve_path(cfg["log_dir"])
            if resolved is not None:
                log_dir = resolved
        if "app_data_dir" in cfg:
            resolved = _resolve_path(cfg["app_data_dir"])
            if resolved is not None:
                app_data_dir = resolved

    db_path = app_data_dir / "edla.db"
    return log_dir, app_data_dir, db_path


# Apply defaults and optional external config
DEFAULT_LOG_DIR, APP_DATA_DIR, EDLA_DB_PATH = _apply_config()
PROFILES_DIR = APP_DATA_DIR / "profiles"

# Optional API/keys from config (not committed). Use for future integrations.
def get_optional_config_key(key: str, default: str = ""):
    """Return optional string value from external config (e.g. api_key). Not committed to repo."""
    cfg = _load_external_config()
    if not cfg or key not in cfg:
        return default
    val = cfg.get(key)
    return str(val).strip() if val is not None else default


# Application logs directory (in same directory as application)
LOGS_DIR = BASE_DIR / "logs"

# Log revalidation timeout (ms) – if exceeded, revalidation is cancelled and user is notified
REVALIDATE_TIMEOUT_MS = 120_000  # 2 minutes

# Ensure directories exist
APP_DATA_DIR.mkdir(exist_ok=True)
PROFILES_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
