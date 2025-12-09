# Architecture Documentation

**Author:** R.W. Harper  
**Last Updated:** 2025-12-09  
**License:** GPL-3.0

## Overview

The Elite Dangerous Log Analyzer (EDLA) is a Python-based GUI application built with PyQt6 for monitoring and analyzing Elite Dangerous journal files in real-time.

## Project Structure

```
EDLA/
├── main.py                 # Main application entry point and GUI
├── config.py               # Configuration and path management
├── profile_manager.py      # Commander profile management
├── log_monitor.py          # Real-time log file monitoring
├── event_tracker.py        # Event tracking and statistics
├── commander_detector.py   # Commander detection from journals
├── requirements.txt        # Python dependencies
├── documents/              # Documentation folder
└── README.md              # Main documentation
```

## Core Components

### Main Application (`main.py`)

- **EliteDangerousApp**: Main QMainWindow class
  - Manages application lifecycle
  - Handles UI updates and navigation
  - Coordinates between components
  - Provides Help menu with About and License dialogs
  - Manages navigation button active states

- **MonitorScreen**: Main monitoring view
  - Displays real-time events
  - Shows monitoring status
  - Commander selection interface

- **ProfileScreen**: Profile management view
  - Lists all commanders
  - Allows manual profile creation
  - Refresh from journal files

### Configuration (`config.py`)

- Defines default paths for:
  - Elite Dangerous log directory
  - Application data directory
  - Profile storage location
- Creates necessary directories on import

### Profile Manager (`profile_manager.py`)

- **CommanderProfile**: Represents a single commander profile
  - Stores preferences, stats, and events
  - JSON-based persistence
  - Event tracking (last 1000 events)

- **ProfileManager**: Manages all profiles
  - Auto-creates profiles from detected commanders
  - Provides profile CRUD operations
  - Handles profile persistence

### Log Monitor (`log_monitor.py`)

- **EliteDangerousLogHandler**: File system event handler
  - Watches for log file changes
  - Parses JSON log entries
  - Extracts commander names from events

- **LogMonitor**: Monitoring coordinator
  - Uses watchdog library for file monitoring
  - Manages observer lifecycle
  - Processes new log entries

### Event Tracker (`event_tracker.py`)

- **EventTracker**: Event processing and statistics
  - Associates events with commanders
  - Updates commander statistics
  - Maintains recent events list
  - Tracks event counts per type

### Commander Detector (`commander_detector.py`)

- **CommanderDetector**: Scans journal files
  - Extracts commander names from LoadGame events
  - Scans all journal files on demand
  - Returns set of unique commanders

## Data Flow

1. **Startup**:
   - Application initializes components
   - CommanderDetector scans journal files
   - ProfileManager auto-creates profiles
   - LogMonitor starts watching directory

2. **Event Processing**:
   - LogMonitor detects file changes
   - Parses JSON log entries
   - Extracts event data and commander name
   - EventTracker processes events for active commander
   - UI updates every second

3. **Profile Management**:
   - User can refresh commanders from journals
   - Profiles auto-created on detection
   - Manual profile creation available
   - All changes persisted to JSON files

## Technology Stack

- **Python 3.8+**: Core language
- **PyQt6**: GUI framework
- **watchdog**: File system monitoring
- **JSON**: Data persistence format

## Design Patterns

- **Observer Pattern**: File system monitoring
- **Singleton-like**: ProfileManager (single instance)
- **MVC-like**: Separation of UI, data, and logic
- **Factory Pattern**: Profile creation

## Future Architecture Considerations

- Plugin system for custom event handlers
- Database backend option (SQLite)
- API layer for external integrations
- Service layer for business logic separation

