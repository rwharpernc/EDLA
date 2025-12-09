"""
Event tracking system for Elite Dangerous events
"""
from typing import Dict, List, Optional
from datetime import datetime
from profile_manager import ProfileManager, CommanderProfile


class EventTracker:
    """Tracks events from Elite Dangerous log files"""
    
    def __init__(self, profile_manager: ProfileManager):
        self.profile_manager = profile_manager
        self.current_commander: Optional[str] = None
        self.recent_events: List[Dict] = []
        self.max_recent_events = 100
    
    def set_current_commander(self, commander_name: str):
        """Set the currently active commander"""
        self.current_commander = commander_name
    
    def process_event(self, event_data: Dict):
        """Process an event from the log monitor"""
        if not self.current_commander:
            return
        
        # Get or create profile for current commander
        profile = self.profile_manager.get_profile(self.current_commander)
        
        # Add event to profile
        profile.add_event(event_data)
        
        # Add to recent events list
        self.recent_events.append(event_data)
        if len(self.recent_events) > self.max_recent_events:
            self.recent_events.pop(0)
        
        # Update stats based on event type
        self.update_stats_from_event(profile, event_data)
    
    def update_stats_from_event(self, profile: CommanderProfile, event_data: Dict):
        """Update commander stats based on event type"""
        event_type = event_data.get("event", "")
        stats = profile.data.get("stats", {})
        
        # Initialize event counters if needed
        if "event_counts" not in stats:
            stats["event_counts"] = {}
        
        # Increment event counter
        stats["event_counts"][event_type] = stats["event_counts"].get(event_type, 0) + 1
        
        # Update last event time
        stats["last_event"] = event_data.get("timestamp", datetime.now().isoformat())
        stats["last_event_type"] = event_type
        
        # Track specific events
        if event_type == "LoadGame":
            raw_data = event_data.get("raw_data", {})
            stats["last_ship"] = raw_data.get("Ship", "Unknown")
            stats["last_system"] = raw_data.get("StarSystem", "Unknown")
        
        profile.update_stats(stats)
    
    def get_recent_events(self, limit: int = 50) -> List[Dict]:
        """Get recent events"""
        return self.recent_events[-limit:]
    
    def get_commander_stats(self, commander_name: str) -> Dict:
        """Get statistics for a commander"""
        profile = self.profile_manager.get_profile(commander_name)
        return profile.data.get("stats", {})

