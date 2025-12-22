# Architecture Documentation

**Author:** R.W. Harper  
**Last Updated:** 2025-12-22  
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
├── session_manager.py      # Session tracking and analysis
├── dashboard_screen.py     # Dashboard UI component
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

- **DashboardScreen**: Session history and statistics view
  - Displays aggregated session statistics
  - Shows session history list
  - Provides session details dialog
  - Filters sessions by commander
  - Manual refresh capability

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

### Session Manager (`session_manager.py`)

- **SessionManager**: Session tracking and analysis
  - Identifies sessions from journal files (each log file = one session)
  - Extracts session metadata (start/end times, commander, jumps, dockings, events)
  - Tracks processed files to prevent duplicate processing
  - Stores session data in JSON format
  - Provides session statistics and filtering
  - Handles both initial scan and incremental updates

### Dashboard Screen (`dashboard_screen.py`)

- **DashboardScreen**: Session visualization UI
  - Displays session statistics (total sessions, jumps, dockings, events)
  - Shows session history list with key information
  - Provides detailed session view dialog
  - Filters sessions by commander
  - Auto-refreshes when new sessions are detected

## Data Flow

1. **Startup**:
   - Application initializes components
   - CommanderDetector scans journal files
   - ProfileManager auto-creates profiles
   - SessionManager scans all existing log files (initial load)
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

4. **Session Tracking**:
   - SessionManager processes log files into sessions
   - Tracks processed files to avoid re-processing
   - Periodically checks for new log files (every 30 seconds)
   - Dashboard displays session statistics and history
   - Sessions filtered by selected commander

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

