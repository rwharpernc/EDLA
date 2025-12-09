"""
Commander detection from Elite Dangerous journal files
"""
import json
from pathlib import Path
from typing import Set, Optional
from config import DEFAULT_LOG_DIR


class CommanderDetector:
    """Detects commanders from Elite Dangerous journal files"""
    
    def __init__(self, log_dir: Path = DEFAULT_LOG_DIR):
        self.log_dir = log_dir
        self.detected_commanders: Set[str] = set()
    
    def scan_journal_files(self) -> Set[str]:
        """Scan all journal files and extract commander names"""
        commanders = set()
        
        if not self.log_dir.exists():
            return commanders
        
        # Scan all .log files in the journal directory
        for log_file in self.log_dir.glob("*.log"):
            commander = self.extract_commander_from_file(log_file)
            if commander:
                commanders.add(commander)
        
        self.detected_commanders = commanders
        return commanders
    
    def extract_commander_from_file(self, log_file: Path) -> Optional[str]:
        """Extract commander name from a journal file"""
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                # Read through the file looking for LoadGame events
                # LoadGame events contain the Commander field
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        event_type = data.get("event", "")
                        
                        # LoadGame event contains commander information
                        if event_type == "LoadGame":
                            commander = data.get("Commander")
                            if commander:
                                return commander
                        
                        # FileHeader event (first line) also contains commander info
                        if event_type == "FileHeader":
                            commander = data.get("part")
                            if commander:
                                # FileHeader part field might contain commander name
                                # But LoadGame is more reliable
                                pass
                    
                    except json.JSONDecodeError:
                        # Skip invalid JSON lines
                        continue
        
        except Exception as e:
            print(f"Error reading journal file {log_file}: {e}")
        
        return None
    
    def get_detected_commanders(self) -> Set[str]:
        """Get the set of detected commanders"""
        return self.detected_commanders.copy()
    
    def scan_and_get_commanders(self) -> Set[str]:
        """Scan files and return commanders"""
        return self.scan_journal_files()

