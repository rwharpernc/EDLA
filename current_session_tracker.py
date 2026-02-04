"""
Current Session Tracker for real-time session statistics
"""
from typing import Dict, List, Optional, Set
from datetime import datetime
from pathlib import Path


def _reputation_text_to_value(text: str) -> Optional[float]:
    """Map Elite Dangerous reputation text to 0-100 scale if known."""
    if not text:
        return None
    t = text.strip().lower()
    # Common journal/UI strings (order: worst to best)
    map_ = {
        "hostile": 0, "unfriendly": 25, "neutral": 50,
        "cordial": 60, "friendly": 75, "allied": 100,
    }
    return map_.get(t)


def _empty_startup_snapshot() -> Dict[str, Dict]:
    return {
        "load_game": {},
        "ranks": {},
        "progress": {},
        "powerplay": {},
        "reputation": {},
    }


class CurrentSessionTracker:
    """Tracks statistics for the current active session in real-time"""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset session statistics (called when new session starts)"""
        self.start_time: Optional[str] = None
        self.commander: Optional[str] = None
        self.current_log_file: Optional[str] = None

        # Credits
        self.start_credits: Optional[int] = None
        self.current_credits: Optional[int] = None
        self.money_earned: int = 0
        self.money_spent: int = 0

        # Travel
        self.light_years_traveled: float = 0.0
        self.jumps: int = 0
        self.systems_visited: Set[str] = set()
        self.stations_visited: Set[str] = set()
        self.planets_landed: int = 0

        # Combat
        self.kills: int = 0
        self.deaths: int = 0
        self.bounties_earned: int = 0
        self.combat_bonds: int = 0

        # Exploration
        self.scans: int = 0
        self.fss_scans: int = 0
        self.dss_scans: int = 0
        self.exploration_value: int = 0

        # Trading
        self.trade_profit: int = 0

        # Missions (counts)
        self.missions_completed: int = 0
        self.mission_rewards: int = 0
        # Active missions (from MissionAccepted; removed on Completed/Failed/Abandoned)
        self.active_missions: List[Dict] = []
        # This session: completed/failed mission summaries
        self.completed_missions: List[Dict] = []
        self.failed_missions: List[Dict] = []

        # Reputation: faction name -> value (journal uses 0-100 or 0.0-1.0)
        self.reputation: Dict[str, float] = {}
        self.startup_snapshot = _empty_startup_snapshot()

        # Ships
        self.first_ship: Optional[str] = None
        self.current_ship: Optional[str] = None
        self.first_system: Optional[str] = None
        self.current_system: Optional[str] = None
    
    def process_event(self, event_data: Dict):
        """Process an event and update current session statistics"""
        event_type = event_data.get("event", "")
        raw_data = event_data.get("raw_data", {})
        timestamp = event_data.get("timestamp", "")
        log_file = event_data.get("log_file", "")
        
        # Detect new session (LoadGame event with different log file)
        if event_type == "LoadGame":
            commander = raw_data.get("Commander")
            if commander and (not self.commander or log_file != self.current_log_file):
                # New session detected - reset and start tracking
                self.reset()
                self.commander = commander
                self.current_log_file = log_file
                self.start_time = timestamp
                self.start_credits = raw_data.get("Credits", 0)
                self.current_credits = self.start_credits
                self.first_ship = raw_data.get("Ship")
                self.current_ship = self.first_ship
                self.first_system = raw_data.get("StarSystem")
                self.current_system = self.first_system
            elif commander == self.commander:
                # Same commander, update current values
                self.current_credits = raw_data.get("Credits", self.current_credits)
                self.current_ship = raw_data.get("Ship", self.current_ship)
                self.current_system = raw_data.get("StarSystem", self.current_system)
        
        # Only process events if we have an active session for this commander
        if not self.commander:
            return
        
        # Track credits changes
        if "Credits" in raw_data:
            new_credits = raw_data.get("Credits", 0)
            if self.current_credits is not None:
                change = new_credits - self.current_credits
                if change > 0:
                    self.money_earned += change
                else:
                    self.money_spent += abs(change)
            self.current_credits = new_credits
        
        # Travel events
        if event_type == "FSDJump":
            self.jumps += 1
            jump_dist = raw_data.get("JumpDist", 0.0)
            if jump_dist:
                self.light_years_traveled += jump_dist
            system = raw_data.get("StarSystem")
            if system:
                self.current_system = system
                self.systems_visited.add(system)
        
        elif event_type == "Location":
            system = raw_data.get("StarSystem")
            if system:
                self.current_system = system
                self.systems_visited.add(system)
        
        elif event_type == "Docked":
            station = raw_data.get("StationName")
            if station:
                self.stations_visited.add(station)
        
        elif event_type == "Touchdown":
            self.planets_landed += 1
        
        # Combat events
        elif event_type == "Bounty":
            reward = raw_data.get("TotalReward", 0)
            if reward:
                self.bounties_earned += reward
                self.kills += 1  # Bounty usually means a kill
        
        elif event_type == "FactionKillBond":
            reward = raw_data.get("Reward", 0)
            if reward:
                self.combat_bonds += reward
                self.kills += 1
        
        elif event_type == "Died":
            self.deaths += 1
        
        # Exploration events
        elif event_type == "Scan":
            self.scans += 1
        
        elif event_type == "FSSBodySignals":
            self.fss_scans += 1
        
        elif event_type == "SAAScanComplete":
            self.dss_scans += 1
        
        elif event_type == "SellExplorationData":
            value = raw_data.get("TotalEarnings", 0)
            if value:
                self.exploration_value += value
        
        # Trading events
        elif event_type == "MarketSell":
            profit = raw_data.get("TotalSale", 0) - raw_data.get("AvgPricePaid", 0) * raw_data.get("Count", 0)
            if profit > 0:
                self.trade_profit += profit
        
        # Mission events
        elif event_type == "MissionAccepted":
            mission_id = raw_data.get("MissionID")
            name = raw_data.get("Name", "")
            faction = raw_data.get("Faction", "")
            expiry = raw_data.get("Expiry", "")
            dest_system = raw_data.get("DestinationSystem", "")
            dest_station = raw_data.get("DestinationStation", "")
            m = {
                "MissionID": mission_id,
                "Name": name,
                "Faction": faction,
                "Expiry": expiry,
                "DestinationSystem": dest_system,
                "DestinationStation": dest_station,
            }
            if mission_id is not None:
                self.active_missions = [x for x in self.active_missions if x.get("MissionID") != mission_id]
            self.active_missions.append(m)

        elif event_type == "MissionCompleted":
            self.missions_completed += 1
            reward = raw_data.get("Reward", 0)
            if reward:
                self.mission_rewards += reward
            mission_id = raw_data.get("MissionID")
            name = raw_data.get("Name", "")
            faction = raw_data.get("Faction", "")
            self.active_missions = [x for x in self.active_missions if x.get("MissionID") != mission_id]

            # Parse FactionEffects (reputation/influence per faction)
            faction_effects = []
            for fe in raw_data.get("FactionEffects") or []:
                if not isinstance(fe, dict):
                    continue
                fname = fe.get("Faction", "")
                rep_trend = fe.get("ReputationTrend", "")
                rep = fe.get("Reputation", "")
                inf_list = fe.get("Influence") or []
                inf_parts = []
                for inf in inf_list:
                    if isinstance(inf, dict):
                        trend = inf.get("Trend", "")
                        inv = inf.get("Influence", "")
                        if inv or trend:
                            inf_parts.append(f"{inv} {trend}".strip() or trend)
                faction_effects.append({
                    "Faction": fname,
                    "ReputationTrend": rep_trend,
                    "Reputation": rep,
                    "Influence": inf_parts,
                })

            # Parse MaterialsReward
            materials_reward = []
            for mat in raw_data.get("MaterialsReward") or []:
                if not isinstance(mat, dict):
                    continue
                mat_name = mat.get("Name_Localised") or mat.get("Name", "")
                mat_cat = mat.get("Category_Localised") or mat.get("Category", "")
                count = mat.get("Count", 0)
                materials_reward.append({"Name": mat_name, "Category": mat_cat, "Count": count})

            self.completed_missions.append({
                "Name": name,
                "Faction": faction,
                "Reward": reward,
                "FactionEffects": faction_effects,
                "MaterialsReward": materials_reward,
            })

        elif event_type == "MissionFailed":
            mission_id = raw_data.get("MissionID")
            name = raw_data.get("Name", "")
            faction = raw_data.get("Faction", "")
            self.active_missions = [x for x in self.active_missions if x.get("MissionID") != mission_id]
            self.failed_missions.append({"Name": name, "Faction": faction})

        elif event_type == "MissionAbandoned":
            mission_id = raw_data.get("MissionID")
            self.active_missions = [x for x in self.active_missions if x.get("MissionID") != mission_id]

        elif event_type == "Rank":
            for k in ("Combat", "Trade", "Explore", "Empire", "Federation", "CQC", "Mercenary", "Exobiologist"):
                v = raw_data.get(k)
                if v is not None:
                    self.startup_snapshot["ranks"][k] = v
        elif event_type == "Progress":
            for k in ("Combat", "Trade", "Explore", "Empire", "Federation", "CQC", "Mercenary", "Exobiologist"):
                v = raw_data.get(k)
                if v is not None:
                    self.startup_snapshot["progress"][k] = v
        elif event_type == "Powerplay":
            self.startup_snapshot["powerplay"] = {
                "Power": raw_data.get("Power"),
                "Rank": raw_data.get("Rank"),
                "Merits": raw_data.get("Merits"),
                "Votes": raw_data.get("Votes"),
                "TimePledged": raw_data.get("TimePledged"),
            }

        # Reputation event (current standings with factions)
        # Journal can send: (1) flat keys with numeric values 0-100 or 0.0-1.0, or
        # (2) a "Factions" array of {"Name": "...", "Reputation": number or "Friendly"/"Allied" etc.}
        elif event_type == "Reputation":
            factions = raw_data.get("Factions")
            if isinstance(factions, list):
                for entry in factions:
                    if not isinstance(entry, dict):
                        continue
                    name = entry.get("Name")
                    rep = entry.get("Reputation")
                    if name is None:
                        continue
                    if isinstance(rep, (int, float)):
                        self.reputation[name] = float(rep)
                    elif isinstance(rep, str):
                        v = _reputation_text_to_value(rep)
                        if v is not None:
                            self.reputation[name] = v
            else:
                for key, value in raw_data.items():
                    if key in ("event", "timestamp", "Factions"):
                        continue
                    try:
                        if isinstance(value, (int, float)):
                            self.reputation[key] = float(value)
                        elif isinstance(value, str):
                            v = _reputation_text_to_value(value)
                            if v is not None:
                                self.reputation[key] = v
                    except (TypeError, ValueError):
                        pass

        # Ship changes
        if "Ship" in raw_data:
            self.current_ship = raw_data.get("Ship", self.current_ship)
    
    def get_statistics(self) -> Dict:
        """Get current session statistics"""
        credits_change = 0
        if self.start_credits is not None and self.current_credits is not None:
            credits_change = self.current_credits - self.start_credits
        
        return {
            "commander": self.commander,
            "start_time": self.start_time,
            "current_system": self.current_system,
            "current_ship": self.current_ship,
            "credits": {
                "start": self.start_credits,
                "current": self.current_credits,
                "change": credits_change,
                "earned": self.money_earned,
                "spent": self.money_spent
            },
            "travel": {
                "light_years": round(self.light_years_traveled, 2),
                "jumps": self.jumps,
                "systems_visited": len(self.systems_visited),
                "stations_visited": len(self.stations_visited),
                "planets_landed": self.planets_landed
            },
            "combat": {
                "kills": self.kills,
                "deaths": self.deaths,
                "bounties_earned": self.bounties_earned,
                "combat_bonds": self.combat_bonds
            },
            "exploration": {
                "scans": self.scans,
                "fss_scans": self.fss_scans,
                "dss_scans": self.dss_scans,
                "exploration_value": self.exploration_value
            },
            "trading": {
                "trade_profit": self.trade_profit
            },
            "missions": {
                "completed": self.missions_completed,
                "rewards": self.mission_rewards,
                "active": list(self.active_missions),
                "completed_list": list(self.completed_missions),
                "failed_list": list(self.failed_missions),
            },
            "reputation": dict(self.reputation),
            "startup_snapshot": {
                "load_game": dict(self.startup_snapshot.get("load_game", {})),
                "ranks": dict(self.startup_snapshot.get("ranks", {})),
                "progress": dict(self.startup_snapshot.get("progress", {})),
                "powerplay": dict(self.startup_snapshot.get("powerplay", {})),
                "reputation": dict(self.startup_snapshot.get("reputation", {})),
            },
        }
    
    def has_active_session(self) -> bool:
        """Check if there's an active session"""
        return self.commander is not None

    def set_startup_snapshot(self, snapshot: Dict) -> None:
        """Set startup snapshot from journal file (e.g. after commander select / revalidation)."""
        if not snapshot:
            return
        for key in ("load_game", "ranks", "progress", "powerplay", "reputation"):
            if key in snapshot and isinstance(snapshot[key], dict):
                self.startup_snapshot[key] = dict(snapshot[key])

