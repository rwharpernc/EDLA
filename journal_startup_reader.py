"""
Read startup sequence from the latest Elite Dangerous journal file.
Captures LoadGame, Rank, Progress, Powerplay, and Reputation written at session start.
"""
import json
from pathlib import Path
from typing import Any, Dict, Optional

from config import DEFAULT_LOG_DIR


def get_startup_snapshot(log_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Read the latest journal file and extract the first LoadGame plus following
    Rank, Progress, Powerplay, and Reputation events (startup sequence).
    Returns a dict with keys: load_game, ranks, progress, powerplay, reputation.
    """
    log_dir = log_dir or DEFAULT_LOG_DIR
    result = {
        "load_game": {},
        "ranks": {},
        "progress": {},
        "powerplay": {},
        "reputation": {},
    }
    if not log_dir.exists():
        return result

    log_files = sorted(log_dir.glob("Journal*.log"), reverse=True)
    if not log_files:
        return result

    latest = log_files[0]
    seen_load_game = False
    try:
        with open(latest, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                event = data.get("event", "")

                if event == "LoadGame":
                    result["load_game"] = {
                        "Commander": data.get("Commander"),
                        "Ship": data.get("Ship"),
                        "ShipID": data.get("ShipID"),
                        "Credits": data.get("Credits"),
                        "Loan": data.get("Loan"),
                        "StarSystem": data.get("StarSystem"),
                        "GameMode": data.get("GameMode"),
                    }
                    seen_load_game = True
                elif event == "Rank":
                    result["ranks"] = {
                        k: data.get(k)
                        for k in ("Combat", "Trade", "Explore", "Empire", "Federation", "CQC", "Mercenary", "Exobiologist")
                        if data.get(k) is not None
                    }
                elif event == "Progress":
                    result["progress"] = {
                        k: data.get(k)
                        for k in ("Combat", "Trade", "Explore", "Empire", "Federation", "CQC", "Mercenary", "Exobiologist")
                        if data.get(k) is not None
                    }
                elif event == "Powerplay":
                    result["powerplay"] = {
                        "Power": data.get("Power"),
                        "Rank": data.get("Rank"),
                        "Merits": data.get("Merits"),
                        "Votes": data.get("Votes"),
                        "TimePledged": data.get("TimePledged"),
                    }
                elif event == "Reputation" and seen_load_game:
                    # Startup Reputation: Empire, Federation, Independent, Alliance (-100 to +100)
                    for key in ("Empire", "Federation", "Independent", "Alliance"):
                        v = data.get(key)
                        if v is not None:
                            result["reputation"][key] = v
    except OSError:
        pass
    return result
