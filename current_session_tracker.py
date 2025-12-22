"""
Current Session Tracker for real-time session statistics
"""
from typing import Dict, Optional, Set
from datetime import datetime
from pathlib import Path


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
        
        # Missions
        self.missions_completed: int = 0
        self.mission_rewards: int = 0
        
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
        elif event_type == "MissionCompleted":
            self.missions_completed += 1
            reward = raw_data.get("Reward", 0)
            if reward:
                self.mission_rewards += reward
        
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
                "rewards": self.mission_rewards
            }
        }
    
    def has_active_session(self) -> bool:
        """Check if there's an active session"""
        return self.commander is not None

