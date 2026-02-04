"""
Read auxiliary Elite Dangerous JSON files from the journal directory.

Elite Dangerous writes Cargo.json, NavRoute.json, and Market.json alongside
journal logs. This module provides a simple way to read them for display or
stats (e.g. current cargo, plotted route, market info).

Ported conceptually from EliteJournalReader (C#) ReadCargoJson, ReadNavRouteJson,
ReadMarketInfo. See documents/JOURNAL_READER_REFERENCE.md.
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import DEFAULT_LOG_DIR


def read_cargo(log_dir: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """
    Read Cargo.json from the Elite Dangerous journal directory.
    Returns parsed dict (e.g. Inventory, Cargo) or None if missing/invalid.
    """
    log_dir = log_dir or DEFAULT_LOG_DIR
    path = log_dir / "Cargo.json"
    return _read_json(path)


def read_nav_route(log_dir: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """
    Read NavRoute.json from the Elite Dangerous journal directory.
    Returns parsed dict (e.g. Route with list of waypoints) or None if missing/invalid.
    """
    log_dir = log_dir or DEFAULT_LOG_DIR
    path = log_dir / "NavRoute.json"
    return _read_json(path)


def read_market(log_dir: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """
    Read Market.json from the Elite Dangerous journal directory.
    Returns parsed dict (market listings, etc.) or None if missing/invalid.
    """
    log_dir = log_dir or DEFAULT_LOG_DIR
    path = log_dir / "Market.json"
    return _read_json(path)


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    """Load a JSON file; return None on missing file or parse error."""
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def get_cargo_summary(log_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Return a small summary of current cargo for UI/stats.
    Keys: count (number of inventory items), total_cargo (total cargo count if present).
    """
    data = read_cargo(log_dir)
    if not data:
        return {"count": 0, "total_cargo": 0}
    inventory = data.get("Inventory") or data.get("Cargo") or []
    if not isinstance(inventory, list):
        return {"count": 0, "total_cargo": 0}
    total = sum((item.get("Count") or 0) for item in inventory if isinstance(item, dict))
    return {"count": len(inventory), "total_cargo": total}


def get_route_waypoints(log_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Return the list of waypoints in the current nav route, or empty list.
    """
    data = read_nav_route(log_dir)
    if not data:
        return []
    route = data.get("Route")
    if not isinstance(route, dict):
        return []
    points = route.get("Route") or route.get("Waypoints") or []
    return points if isinstance(points, list) else []
