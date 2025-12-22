"""
Session Manager for tracking Elite Dangerous game sessions
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
from config import DEFAULT_LOG_DIR, APP_DATA_DIR


class SessionManager:
    """Manages game sessions from journal log files"""
    
    def __init__(self, log_dir: Path = DEFAULT_LOG_DIR):
        self.log_dir = log_dir
        self.sessions_file = APP_DATA_DIR / "sessions.json"
        self.processed_files_file = APP_DATA_DIR / "processed_files.json"
        self.sessions: Dict[str, Dict] = {}  # session_id -> session_data
        self.processed_files: Set[str] = set()  # Set of processed file paths
        
        # Load existing data
        self.load_sessions()
        self.load_processed_files()
    
    def load_sessions(self):
        """Load sessions from disk"""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.sessions = data.get("sessions", {})
            except Exception as e:
                print(f"Error loading sessions: {e}")
                self.sessions = {}
    
    def save_sessions(self):
        """Save sessions to disk"""
        try:
            data = {
                "sessions": self.sessions,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving sessions: {e}")
    
    def load_processed_files(self):
        """Load list of processed files"""
        if self.processed_files_file.exists():
            try:
                with open(self.processed_files_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.processed_files = set(data.get("processed_files", []))
            except Exception as e:
                print(f"Error loading processed files: {e}")
                self.processed_files = set()
    
    def save_processed_files(self):
        """Save list of processed files"""
        try:
            data = {
                "processed_files": list(self.processed_files),
                "last_updated": datetime.now().isoformat()
            }
            with open(self.processed_files_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving processed files: {e}")
    
    def get_session_id_from_file(self, log_file: Path) -> str:
        """Generate a unique session ID from log file name"""
        # Use the file name as session ID (it contains timestamp)
        return log_file.name
    
    def parse_timestamp_from_filename(self, filename: str) -> Optional[datetime]:
        """Extract timestamp from journal filename"""
        # Journal.YYYYMMDDHHMMSS.01.log
        match = re.search(r'Journal\.(\d{14})\.', filename)
        if match:
            try:
                timestamp_str = match.group(1)
                return datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
            except ValueError:
                return None
        return None
    
    def scan_all_logs(self, force_rescan: bool = False):
        """Scan all log files and extract session data"""
        try:
            if not self.log_dir.exists():
                return
            
            log_files = list(self.log_dir.glob("*.log"))
            new_sessions = 0
            
            for log_file in sorted(log_files):
                try:
                    file_path_str = str(log_file)
                    
                    # Skip if already processed (unless force rescan)
                    if not force_rescan and file_path_str in self.processed_files:
                        continue
                    
                    # Process the log file
                    session_data = self.process_log_file(log_file)
                    if session_data:
                        session_id = self.get_session_id_from_file(log_file)
                        self.sessions[session_id] = session_data
                        self.processed_files.add(file_path_str)
                        new_sessions += 1
                except Exception as e:
                    print(f"Error processing log file {log_file}: {e}")
                    continue
            
            if new_sessions > 0:
                self.save_sessions()
                self.save_processed_files()
                print(f"Processed {new_sessions} new session(s)")
        except Exception as e:
            print(f"Error in scan_all_logs: {e}")
            import traceback
            traceback.print_exc()
    
    def process_log_file(self, log_file: Path) -> Optional[Dict]:
        """Process a single log file and extract session data"""
        if not log_file.exists():
            return None
        
        session_id = self.get_session_id_from_file(log_file)
        session_start = self.parse_timestamp_from_filename(log_file.name)
        
        session_data = {
            "session_id": session_id,
            "log_file": str(log_file),
            "start_time": session_start.isoformat() if session_start else None,
            "end_time": None,
            "commander": None,
            "events": [],
            "event_counts": {},
            "first_ship": None,
            "last_ship": None,
            "first_system": None,
            "last_system": None,
            "first_credits": None,
            "last_credits": None,
            "credits_change": 0,
            "jumps": 0,
            "light_years_traveled": 0.0,
            "docked_count": 0,
            "undocked_count": 0,
            "planets_landed": 0,
            "total_events": 0,
            # Combat statistics
            "bounties_earned": 0,
            "bounty_count": 0,
            "combat_bonds": 0,
            "died": False,
            "kills": 0,
            "deaths": 0,
            # Exploration statistics
            "scans": 0,
            "fss_scans": 0,
            "dss_scans": 0,
            "codex_entries": 0,
            "exploration_value": 0,
            # Trading statistics
            "market_buys": 0,
            "market_sells": 0,
            "trade_profit": 0,
            # Mission statistics
            "missions_accepted": 0,
            "missions_completed": 0,
            "missions_failed": 0,
            "mission_rewards": 0,
            # Location tracking
            "systems_visited": set(),
            "stations_visited": set(),
            "unique_ships": set(),
            # Rank tracking (if available)
            "start_ranks": {},
            "end_ranks": {},
        }
        
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                last_timestamp = None
                
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        event_type = data.get("event", "")
                        timestamp = data.get("timestamp", "")
                        
                        if timestamp:
                            last_timestamp = timestamp
                        
                        # Track event
                        session_data["events"].append({
                            "event": event_type,
                            "timestamp": timestamp,
                            "data": data
                        })
                        session_data["total_events"] += 1
                        
                        # Count events
                        session_data["event_counts"][event_type] = \
                            session_data["event_counts"].get(event_type, 0) + 1
                        
                        # Extract key information
                        if event_type == "LoadGame":
                            if not session_data["commander"]:
                                session_data["commander"] = data.get("Commander")
                            if not session_data["first_ship"]:
                                session_data["first_ship"] = data.get("Ship")
                            if not session_data["first_system"]:
                                session_data["first_system"] = data.get("StarSystem")
                            if session_data["first_credits"] is None:
                                session_data["first_credits"] = data.get("Credits", 0)
                            
                            # Track ranks at start
                            if "Rank" in data:
                                session_data["start_ranks"]["combat"] = data.get("Rank", 0)
                            if "TradeRank" in data:
                                session_data["start_ranks"]["trade"] = data.get("TradeRank", 0)
                            if "ExploreRank" in data:
                                session_data["start_ranks"]["exploration"] = data.get("ExploreRank", 0)
                            if "EmpireRank" in data:
                                session_data["start_ranks"]["empire"] = data.get("EmpireRank", 0)
                            if "FederationRank" in data:
                                session_data["start_ranks"]["federation"] = data.get("FederationRank", 0)
                        
                        elif event_type == "FSDJump":
                            session_data["jumps"] += 1
                            jump_dist = data.get("JumpDist", 0.0)
                            if jump_dist:
                                session_data["light_years_traveled"] += jump_dist
                            system = data.get("StarSystem")
                            if system:
                                session_data["last_system"] = system
                                session_data["systems_visited"].add(system)
                        
                        elif event_type == "Location":
                            system = data.get("StarSystem")
                            if system:
                                if not session_data["last_system"]:
                                    session_data["last_system"] = system
                                session_data["systems_visited"].add(system)
                        
                        elif event_type == "Docked":
                            session_data["docked_count"] += 1
                            station = data.get("StationName")
                            if station:
                                session_data["stations_visited"].add(station)
                        
                        elif event_type == "Undocked":
                            session_data["undocked_count"] += 1
                        
                        elif event_type == "Touchdown":
                            session_data["planets_landed"] += 1
                        
                        elif event_type == "Bounty":
                            reward = data.get("TotalReward", 0)
                            if reward:
                                session_data["bounties_earned"] += reward
                                session_data["bounty_count"] += 1
                        
                        elif event_type == "FactionKillBond":
                            reward = data.get("Reward", 0)
                            if reward:
                                session_data["combat_bonds"] += reward
                        
                        elif event_type == "Died":
                            session_data["died"] = True
                            session_data["deaths"] += 1
                        
                        elif event_type == "ShipTargeted":
                            # Track kills
                            if data.get("TargetLocked", False):
                                pass  # Could track targets
                        
                        elif event_type == "Scan":
                            session_data["scans"] += 1
                        
                        elif event_type == "FSSBodySignals":
                            session_data["fss_scans"] += 1
                        
                        elif event_type == "SAAScanComplete":
                            session_data["dss_scans"] += 1
                        
                        elif event_type == "CodexEntry":
                            session_data["codex_entries"] += 1
                        
                        elif event_type == "SellExplorationData":
                            value = data.get("TotalEarnings", 0)
                            if value:
                                session_data["exploration_value"] += value
                        
                        elif event_type == "MarketBuy":
                            session_data["market_buys"] += 1
                        
                        elif event_type == "MarketSell":
                            session_data["market_sells"] += 1
                            profit = data.get("TotalSale", 0) - data.get("AvgPricePaid", 0) * data.get("Count", 0)
                            if profit > 0:
                                session_data["trade_profit"] += profit
                        
                        elif event_type == "MissionAccepted":
                            session_data["missions_accepted"] += 1
                        
                        elif event_type == "MissionCompleted":
                            session_data["missions_completed"] += 1
                            reward = data.get("Reward", 0)
                            if reward:
                                session_data["mission_rewards"] += reward
                        
                        elif event_type == "MissionFailed":
                            session_data["missions_failed"] += 1
                        
                        elif event_type == "Promotion":
                            # Track rank changes
                            rank_type = data.get("Rank")
                            if rank_type:
                                if "Combat" in rank_type:
                                    session_data["end_ranks"]["combat"] = data.get("NewRank", 0)
                                elif "Trade" in rank_type:
                                    session_data["end_ranks"]["trade"] = data.get("NewRank", 0)
                                elif "Exploration" in rank_type:
                                    session_data["end_ranks"]["exploration"] = data.get("NewRank", 0)
                        
                        # Update last ship if available
                        if "Ship" in data:
                            ship = data.get("Ship")
                            if ship:
                                session_data["last_ship"] = ship
                                session_data["unique_ships"].add(ship)
                        
                        # Update last credits if available
                        if "Credits" in data:
                            session_data["last_credits"] = data.get("Credits", 0)
                    
                    except json.JSONDecodeError:
                        continue
                
                # Set end time to last event timestamp
                if last_timestamp:
                    session_data["end_time"] = last_timestamp
                
                # Calculate credits change
                if session_data["first_credits"] is not None and session_data["last_credits"] is not None:
                    session_data["credits_change"] = session_data["last_credits"] - session_data["first_credits"]
                
                # Convert sets to lists for JSON serialization
                session_data["systems_visited"] = list(session_data["systems_visited"])
                session_data["stations_visited"] = list(session_data["stations_visited"])
                session_data["unique_ships"] = list(session_data["unique_ships"])
                
                # Keep only essential events to prevent bloat (keep first 100 and last 100)
                if len(session_data["events"]) > 200:
                    session_data["events"] = (
                        session_data["events"][:100] + 
                        session_data["events"][-100:]
                    )
                    session_data["events_summary"] = f"Total: {session_data['total_events']} events (showing first 100 and last 100)"
                
                return session_data
        
        except Exception as e:
            print(f"Error processing log file {log_file}: {e}")
            return None
    
    def process_new_log_file(self, log_file: Path):
        """Process a new log file (called when file is modified)"""
        file_path_str = str(log_file)
        
        # Skip if already processed
        if file_path_str in self.processed_files:
            return
        
        session_data = self.process_log_file(log_file)
        if session_data:
            session_id = self.get_session_id_from_file(log_file)
            self.sessions[session_id] = session_data
            self.processed_files.add(file_path_str)
            self.save_sessions()
            self.save_processed_files()
    
    def get_sessions_for_commander(self, commander_name: str) -> List[Dict]:
        """Get all sessions for a specific commander"""
        sessions = []
        for session_id, session_data in self.sessions.items():
            if session_data.get("commander") == commander_name:
                sessions.append(session_data)
        
        # Sort by start time (newest first), handling None values
        def sort_key(x):
            start_time = x.get("start_time")
            # Return empty string for None to sort them last
            return start_time if start_time else ""
        
        sessions.sort(key=sort_key, reverse=True)
        return sessions
    
    def get_all_sessions(self, limit: Optional[int] = None) -> List[Dict]:
        """Get all sessions, optionally limited"""
        sessions = list(self.sessions.values())
        
        # Sort by start time (newest first), handling None values
        def sort_key(x):
            start_time = x.get("start_time")
            # Return empty string for None to sort them last
            return start_time if start_time else ""
        
        sessions.sort(key=sort_key, reverse=True)
        
        if limit:
            return sessions[:limit]
        return sessions
    
    def get_session_statistics(self, commander_name: Optional[str] = None) -> Dict:
        """Get aggregated statistics for sessions"""
        sessions = self.get_sessions_for_commander(commander_name) if commander_name else self.get_all_sessions()
        
        if not sessions:
            return {
            "total_sessions": 0,
            "total_jumps": 0,
            "total_light_years": 0.0,
            "total_docked": 0,
            "total_planets_landed": 0,
            "total_events": 0,
            "total_credits_change": 0,
            "total_kills": 0,
            "total_deaths": 0,
                "total_bounties": 0,
                "total_combat_bonds": 0,
                "total_exploration_value": 0,
                "total_trade_profit": 0,
                "total_mission_rewards": 0,
                "total_systems_visited": 0,
                "total_stations_visited": 0,
                "total_scans": 0,
                "total_missions_completed": 0,
                "deaths": 0
            }
        
        # Aggregate all statistics
        all_systems = set()
        all_stations = set()
        
        for s in sessions:
            all_systems.update(s.get("systems_visited", []))
            all_stations.update(s.get("stations_visited", []))
        
        stats = {
            "total_sessions": len(sessions),
            "total_jumps": sum(s.get("jumps", 0) for s in sessions),
            "total_light_years": round(sum(s.get("light_years_traveled", 0.0) for s in sessions), 2),
            "total_docked": sum(s.get("docked_count", 0) for s in sessions),
            "total_planets_landed": sum(s.get("planets_landed", 0) for s in sessions),
            "total_events": sum(s.get("total_events", 0) for s in sessions),
            "total_kills": sum(s.get("kills", 0) for s in sessions),
            "total_deaths": sum(1 for s in sessions if s.get("died", False)),
            "total_credits_change": sum(s.get("credits_change", 0) for s in sessions),
            "total_bounties": sum(s.get("bounties_earned", 0) for s in sessions),
            "total_combat_bonds": sum(s.get("combat_bonds", 0) for s in sessions),
            "total_exploration_value": sum(s.get("exploration_value", 0) for s in sessions),
            "total_trade_profit": sum(s.get("trade_profit", 0) for s in sessions),
            "total_mission_rewards": sum(s.get("mission_rewards", 0) for s in sessions),
            "total_systems_visited": len(all_systems),
            "total_stations_visited": len(all_stations),
            "total_scans": sum(s.get("scans", 0) for s in sessions),
            "total_fss_scans": sum(s.get("fss_scans", 0) for s in sessions),
            "total_dss_scans": sum(s.get("dss_scans", 0) for s in sessions),
            "total_codex_entries": sum(s.get("codex_entries", 0) for s in sessions),
            "total_missions_accepted": sum(s.get("missions_accepted", 0) for s in sessions),
            "total_missions_completed": sum(s.get("missions_completed", 0) for s in sessions),
            "total_missions_failed": sum(s.get("missions_failed", 0) for s in sessions),
            "deaths": sum(1 for s in sessions if s.get("died", False)),
            "first_session": sessions[-1].get("start_time") if sessions else None,
            "last_session": sessions[0].get("start_time") if sessions else None
        }
        
        return stats

