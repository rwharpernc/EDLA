"""
Profile Manager for Elite Dangerous commanders
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from config import PROFILES_DIR


class CommanderProfile:
    """Represents a commander profile"""
    
    def __init__(self, commander_name: str, profile_data: Optional[Dict] = None):
        self.commander_name = commander_name
        self.profile_file = PROFILES_DIR / f"{commander_name}.json"
        
        if profile_data:
            self.data = profile_data
        else:
            self.data = {
                "commander_name": commander_name,
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "preferences": {},
                "stats": {},
                "tracked_events": []
            }
    
    def save(self):
        """Save profile to disk"""
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.profile_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def load(self):
        """Load profile from disk. Returns False if file is missing or invalid JSON."""
        if not self.profile_file.exists():
            return False
        try:
            with open(self.profile_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            return True
        except json.JSONDecodeError as e:
            # Corrupted or malformed JSON - skip this profile so the app doesn't crash
            print(f"Invalid JSON in profile {self.profile_file.name}: {e}")
            return False
        except Exception as e:
            print(f"Error loading profile {self.profile_file.name}: {e}")
            return False
    
    def add_event(self, event_data: Dict):
        """Add a tracked event to the profile"""
        event_data["timestamp"] = datetime.now().isoformat()
        self.data["tracked_events"].append(event_data)
        # Keep only last 1000 events to prevent file bloat
        if len(self.data["tracked_events"]) > 1000:
            self.data["tracked_events"] = self.data["tracked_events"][-1000:]
        self.save()
    
    def update_stats(self, stats: Dict):
        """Update commander statistics"""
        self.data["stats"].update(stats)
        self.save()
    
    def update_preferences(self, preferences: Dict):
        """Update commander preferences"""
        self.data["preferences"].update(preferences)
        self.save()


class ProfileManager:
    """Manages all commander profiles"""
    
    def __init__(self, auto_detect_commanders: bool = True):
        self.profiles: Dict[str, CommanderProfile] = {}
        self.load_all_profiles()
        
        # Auto-detect commanders from journal files
        if auto_detect_commanders:
            self.auto_create_profiles_from_journals()
    
    def load_all_profiles(self):
        """Load all existing profiles"""
        for profile_file in PROFILES_DIR.glob("*.json"):
            commander_name = profile_file.stem
            profile = CommanderProfile(commander_name)
            if profile.load():
                self.profiles[commander_name] = profile
    
    def auto_create_profiles_from_journals(self):
        """Automatically create profiles for commanders found in journal files"""
        from commander_detector import CommanderDetector
        
        detector = CommanderDetector()
        detected_commanders = detector.scan_journal_files()
        
        # Create profiles for any commanders we found that don't exist yet
        for commander_name in detected_commanders:
            if commander_name not in self.profiles:
                profile = CommanderProfile(commander_name)
                profile.save()
                self.profiles[commander_name] = profile
                print(f"Auto-created profile for commander: {commander_name}")
    
    def refresh_from_journals(self):
        """Refresh commander list by scanning journal files again"""
        self.auto_create_profiles_from_journals()
    
    def get_profile(self, commander_name: str) -> CommanderProfile:
        """Get a profile, creating it if it doesn't exist"""
        if commander_name not in self.profiles:
            profile = CommanderProfile(commander_name)
            profile.save()
            self.profiles[commander_name] = profile
        return self.profiles[commander_name]
    
    def list_profiles(self) -> List[str]:
        """List all profile names"""
        return sorted(list(self.profiles.keys()))
    
    def delete_profile(self, commander_name: str) -> bool:
        """Delete a profile"""
        if commander_name in self.profiles:
            profile = self.profiles[commander_name]
            if profile.profile_file.exists():
                profile.profile_file.unlink()
            del self.profiles[commander_name]
            return True
        return False

