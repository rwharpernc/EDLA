# Architecture Documentation

**Author:** R.W. Harper  
**Last Updated:** 2026-02-12  
**License:** GPL-3.0

**Note (2026-02-12):** This version has not been fully tested.

## Overview

The Elite Dangerous Log Analyzer (EDLA) is a Python-based GUI application built with PyQt6 for monitoring and analyzing Elite Dangerous journal files in real-time.

## Project Structure

```
EDLA/
├── main.py                     # Main entry point; bootstrap (config setup if no edla_config.json), then GUI
├── config.py                   # Configuration and path management (loads edla_config.json when present)
├── config_setup.py             # Interactive first-run config dialog (paths, optional API key)
├── edla_config.sample.json     # Sample config; copy to edla_config.json (do not commit)
├── profile_manager.py          # Commander profile management
├── log_monitor.py              # Real-time log file monitoring
├── event_tracker.py             # Event tracking and statistics
├── commander_detector.py        # Commander detection from journals
├── session_manager.py          # Session tracking and analysis (SQLite)
├── dashboard_screen.py         # Dashboard UI component
├── missions_reputation_screen.py  # Missions & Reputation view
├── journal_aux_reader.py       # Cargo/NavRoute/Market JSON reader
├── journal_startup_reader.py   # Startup snapshot (LoadGame, Rank, Progress, Powerplay, Reputation) from latest journal
├── current_session_tracker.py  # Real-time session and mission/reputation tracking
├── no_journal_widget.py        # No-journal-files informational widget
├── requirements.txt            # Python dependencies
├── documents/                  # Documentation folder (includes CONFIG.md for setup and clean-repo list)
└── README.md                   # Main documentation
```

## Core Components

### Main Application (`main.py`)

- **EliteDangerousApp**: Main QMainWindow class
  - Manages application lifecycle
  - Handles UI updates and navigation
  - Coordinates between components
  - Provides Help menu with About and License dialogs
  - Manages navigation button active states
  - Resizable window with scrollable content panels

- **HomeScreen**: Start view; when a commander is selected, shows welcome and startup snapshot (ranks with in-game names, progress %, powerplay, superpower reputation, last session start). Refreshes from tracker when Home tab is visible so new journal data appears.

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

- **MissionsReputationScreen** (`missions_reputation_screen.py`): Missions and reputation view
  - Superpower Reputation Checkpoint Progress (fixed pane at top; data from Reputation event)
  - Completed missions ready to turn in, completed/failed this session
  - Refreshes only when data changes to keep the app responsive

### Configuration (`config.py`)

- Does not embed local paths or API keys. Optional external config: `edla_config.json` in the application directory (see `edla_config.sample.json` and [CONFIG.md](CONFIG.md)); do not commit `edla_config.json`.
- Defines default paths when config is absent or keys are empty:
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
  - **Stores session data and processed-file list in SQLite** (`%USERPROFILE%\.edla\edla.db`)
  - Automatically migrates from legacy `sessions.json` / `processed_files.json` on first run
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
- **SQLite** (stdlib): Session and processed-file persistence (`edla.db`)
- **JSON**: Commander profile files in `profiles/`; journal events are line-delimited JSON

## Design Patterns

- **Observer Pattern**: File system monitoring
- **Singleton-like**: ProfileManager (single instance)
- **MVC-like**: Separation of UI, data, and logic
- **Factory Pattern**: Profile creation

## Future Architecture Considerations

- Plugin system for custom event handlers
- API layer for external integrations
- Service layer for business logic separation

