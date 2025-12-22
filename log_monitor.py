"""
Log file monitor for Elite Dangerous log files
"""
import json
import re
from pathlib import Path
from typing import Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent
from config import DEFAULT_LOG_DIR


class EliteDangerousLogHandler(FileSystemEventHandler):
    """Handles file system events for Elite Dangerous log files"""
    
    def __init__(self, on_event: Callable, log_dir: Path = DEFAULT_LOG_DIR):
        super().__init__()
        self.on_event = on_event
        self.log_dir = log_dir
        self.processed_positions = {}  # Track file positions to avoid re-processing
    
    def on_modified(self, event):
        """Called when a log file is modified"""
        if not event.is_directory and event.src_path.endswith('.log'):
            self.process_log_file(Path(event.src_path))
    
    def on_created(self, event):
        """Called when a new log file is created"""
        if not event.is_directory and event.src_path.endswith('.log'):
            # Process the new file
            self.process_log_file(Path(event.src_path))
    
    def process_log_file(self, log_file: Path):
        """Process new lines in a log file"""
        if not log_file.exists():
            return
        
        # Get current position in file
        current_pos = self.processed_positions.get(str(log_file), 0)
        
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(current_pos)
                new_lines = f.readlines()
                self.processed_positions[str(log_file)] = f.tell()
                
                for line in new_lines:
                    event_data = self.parse_log_line(line.strip(), log_file)
                    if event_data:
                        self.on_event(event_data)
        except Exception as e:
            print(f"Error processing log file {log_file}: {e}")
    
    def parse_log_line(self, line: str, log_file: Path) -> Optional[dict]:
        """Parse a single line from the log file"""
        if not line:
            return None
        
        # Elite Dangerous log files are JSON format
        try:
            data = json.loads(line)
            event_data = {
                "event": data.get("event", "Unknown"),
                "timestamp": data.get("timestamp", ""),
                "raw_data": data,
                "log_file": str(log_file),
                "commander": self.extract_commander_from_event(data)
            }
            return event_data
        except json.JSONDecodeError:
            # Not a JSON line, might be a header or other format
            return None
    
    def extract_commander_from_event(self, event_data: dict) -> Optional[str]:
        """Extract commander name from event data"""
        # LoadGame events contain the Commander field
        if event_data.get("event") == "LoadGame":
            return event_data.get("Commander")
        return None
    
    def scan_existing_logs(self):
        """Scan existing log files for initial load"""
        if not self.log_dir.exists():
            return
        
        for log_file in self.log_dir.glob("*.log"):
            self.process_log_file(log_file)


class LogMonitor:
    """Monitors Elite Dangerous log directory for changes"""
    
    def __init__(self, on_event: Callable, log_dir: Path = DEFAULT_LOG_DIR):
        self.log_dir = log_dir
        self.observer = None
        self.handler = EliteDangerousLogHandler(on_event, log_dir)
        self.is_monitoring = False
    
    def start(self):
        """Start monitoring the log directory"""
        if self.is_monitoring:
            return
        
        if not self.log_dir.exists():
            print(f"Warning: Log directory does not exist: {self.log_dir}")
            return
        
        self.observer = Observer()
        self.observer.schedule(self.handler, str(self.log_dir), recursive=False)
        self.observer.start()
        self.is_monitoring = True
        
        # Scan existing logs
        self.handler.scan_existing_logs()
        
        print(f"Started monitoring: {self.log_dir}")
    
    def stop(self):
        """Stop monitoring"""
        if self.observer and self.is_monitoring:
            self.observer.stop()
            self.observer.join()
            self.is_monitoring = False
            print("Stopped monitoring")

