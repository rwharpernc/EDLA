# Changelog

**Author:** R.W. Harper  
**Last Updated:** 2025-02-04  
**License:** GPL-3.0

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- Next version starts next session.

## [Alpha 1.03] - 2025-02-04

### Added
- **Home page** – App starts on a Home screen with “Select a commander first”; welcome message when a commander is selected.
- **Commander switching bar** – Nav bar combo box to switch commanders; refresh button to rescan from journals.
- **Log revalidation on commander selection** – When a commander is selected, all logs are revalidated in the background; status bar shows “Revalidating logs…” then “Logs revalidated.”
- **Verbose log view** – Monitor events show detailed one-line descriptions (FSDJump, Docked, missions, Powerplay, Rank, Progress, etc.). Newest first; generic fallback shows all fields for unknown events.
- **Journal reference docs** – EliteJournalReader and ODEliteTracker referenced in `documents/JOURNAL_READER_REFERENCE.md` for porting ideas.
- **Auxiliary JSON reader** (`journal_aux_reader.py`) – Reads Cargo.json, NavRoute.json, Market.json from the journal directory.
- **Mission and reputation tracking** – Current session tracker records active missions, completed/failed this session, and faction reputation from journal events.
- **Missions & Reputation view** – New “Missions” tab with full-page view of active missions, completed/failed this session, and reputation; updates live.
- **Full window resizing** – Window is resizable (min 500×400); content area uses stretch so panels resize with the window.
- **Auto-scrolling** – Monitor, Profiles, Dashboard, and Missions views use scroll areas so content scrolls when the view is smaller than the content.
- **Rank names (in-game)** – All rank categories use correct Elite Dangerous titles: Combat (Harmless→Elite), Trade (Penniless→Elite), Exploration (Aimless→Elite), CQC (Helpless→Elite), Mercenary (Odyssey), Exobiologist (Odyssey), Federation Navy, Empire Navy; Alliance noted as reputation only.
- **Odyssey ranks** – Mercenary and Exobiologist ranks supported in startup snapshot, tracker, and Home/Monitor display.

### Changed
- **Session and processed-file storage** – Switched from JSON files to SQLite (`edla.db`); migration from legacy JSON on first run.
- **Defensive JSON handling** – Profile and session load paths catch invalid JSON so the app does not crash on corrupted files.
- **UI update interval** – Refresh timer 3s; only visible tab updated; missions/reputation rebuild only when data changes.
- **Reputation parsing** – Support for flat key-value and `Factions` array; text levels (Friendly, Allied) mapped to 0–100.
- **Documentation** – All docs updated for Alpha 1.03 (2025-02-04).

### Fixed
- **Large JSON crash** – Corrupted or oversized `sessions.json` / profile JSON no longer crashes the app; errors are handled and optional backup is made.
- **Reputation pane** – Robust parsing of Reputation event so data populates when the game sends it.
- **Graceful exit** – Close button and File→Exit stop timers, revalidation thread, and log monitor cleanly.

---

## [Alpha 1.0] - 2025-12-22

### Added
- **SQLite session storage** - Session and processed-file data now use SQLite
  - Database file: `%USERPROFILE%\.edla\edla.db`
  - No large JSON files; better performance and reliability at scale
  - Automatic migration: existing `sessions.json` and `processed_files.json` are imported on first run and renamed to `.json.migrated`
  - Uses Python standard library (`sqlite3`) — no new dependencies
- **Enhanced Session Dashboard** - Comprehensive dashboard with dual view modes
  - **Current Session View** - Real-time statistics for active game session
    - Live tracking of credits, money earned/spent, light years traveled
    - Real-time updates for jumps, systems visited, stations visited, planets landed
    - Combat statistics: kills, deaths, bounties, combat bonds
    - Updates automatically as you play
  - **Historical View** - Aggregated statistics across all past sessions
    - Tabbed interface: Overview, Combat, Exploration, Trading, Missions
    - Comprehensive session history list with detailed information
    - Session details dialog with full breakdown (double-click to view)
    - Commander filtering (shows only selected commander's sessions)
  - View mode toggle buttons (Current Session / Historical)
  - Automatic refresh when new sessions detected
  - Manual refresh button to rescan all logs
- **Current Session Tracker** (`current_session_tracker.py`) - Real-time session statistics
  - Tracks active game session in real-time
  - Monitors: credits, money earned/spent, light years, jumps, systems, stations, planets, kills, deaths
  - Updates automatically as events occur
  - Provides live data for Current Session dashboard view
- **Enhanced Session Tracking** - Expanded session data collection
  - Money earned/spent tracking from credit changes
  - Light years traveled (sum of jump distances)
  - Planets landed tracking (Touchdown events)
  - Kills and deaths tracking (separate counters)
  - Comprehensive combat, exploration, trading, and mission statistics
  - Enhanced session details with all tracked metrics
- **No Journal Files Widget** (`no_journal_widget.py`) - Elegant informational display
  - Reusable widget shown when journal files don't exist
  - Provides helpful instructions and expected file location
  - Integrated into Monitor, Profiles, and Dashboard screens
  - Prevents confusion when Elite Dangerous hasn't been played yet
- **Comprehensive Exception Handling** - Robust error handling and logging
  - Global exception handler to catch all uncaught exceptions
  - Detailed error logging with full tracebacks
  - Error messages written to log files even if logging fails
  - Initialization error handling with step-by-step logging
  - UI update error handling to prevent crashes
  - Error dialog shown to users on fatal crashes
- **Batch File Logging** - Enhanced `run.bat` with comprehensive logging
  - Timestamped log files for each run (`logs/run_YYYYMMDD_HHMMSS.log`)
  - Captures all output including dependency installation
  - Aggregated error log (`logs/error.log`) for quick crash reference
  - Logs exit codes and error messages
  - User-friendly error messages pointing to log files
- **Application Logging** - Improved logging system
  - Logs stored in application directory (`logs/app.log`)
  - Startup/shutdown logging with timestamps
  - Step-by-step initialization logging
  - Error logging with full tracebacks
  - UTF-8 encoding support
- **Session Manager** (`session_manager.py`) - Core session tracking system
  - Identifies sessions from journal files (each log file = one session)
  - Extracts comprehensive session metadata
  - Tracks processed files to prevent duplicate processing
  - Provides session statistics and filtering capabilities
  - Enhanced with money, light years, planets, kills, deaths tracking
- **Dashboard Screen** (`dashboard_screen.py`) - UI component for session visualization
  - Dual view mode support (Current Session / Historical)
  - Tabbed statistics display for historical data
  - Session list with detailed information
  - Session details dialog
- **File creation event handling** in log monitor for immediate new file detection
- **Comprehensive Documentation** - New and updated documentation
  - **HOW_IT_WORKS.md** - Detailed technical documentation explaining architecture, data flow, expected results, and troubleshooting
  - Updated USER_GUIDE.md with expected behavior sections
  - Updated README.md with "How It Works" section and data flow diagram

### Changed
- **Session and processed-file storage** - Switched from JSON files to SQLite
  - `sessions.json` and `processed_files.json` replaced by `edla.db`
  - Setup and run batch files updated to mention SQLite storage
  - All documentation updated (README, ARCHITECTURE, HOW_IT_WORKS, USER_GUIDE, DEVELOPER_GUIDE, BUILD_GUIDE)
- **Log File Location** - Application logs now stored in application directory
  - Changed from `%USERPROFILE%\.edla\logs\app.log` to `logs/app.log` (relative to app)
  - Keeps logs with application for easier access and management
  - Updated documentation to reflect new location
- **Session Manager** - Enhanced with comprehensive statistics tracking
  - Expanded session data to include money earned/spent, light years, planets, kills, deaths
  - Improved error handling in session scanning
  - Better handling of None values in session sorting
- **Dashboard Screen** - Major UI enhancement
  - Added dual view mode (Current Session / Historical)
  - Reorganized statistics into logical tabs
  - Enhanced session list with more detailed information
  - Improved session details dialog with all tracked metrics
- **Initial Session Scan** - Deferred to prevent UI blocking
  - Uses QTimer.singleShot to defer heavy log scanning
  - Allows UI to initialize first before processing logs
  - Prevents application appearing frozen on startup
- **Error Handling** - Comprehensive error handling throughout
  - All major operations wrapped in try-except blocks
  - Detailed error logging at every step
  - Graceful degradation when errors occur
- Initial project setup with PyQt6 GUI framework
- Real-time log file monitoring using watchdog
- Commander profile management system
- Automatic commander detection from Elite Dangerous journal files
- Event tracking and statistics per commander
- Dark-themed modern UI
- Profile screen for managing commanders
- Monitor screen for viewing real-time events
- Commander selection menu
- Journal file scanning to auto-detect commanders
- Navigation button highlighting (active screen indicator)
- Help menu with About and License dialogs
- Copyright information in window title
- Full GPL-3.0 license display
- Build infrastructure for Windows executables (PyInstaller)
- Inno Setup installer script template
- Comprehensive documentation (User Guide, Developer Guide, Build Guide, Architecture, Journal Format, How It Works)

### Fixed
- **Critical Crashes** - Fixed multiple application crashes
  - Fixed `QListWidgetItem.setStyleSheet()` AttributeError - QListWidgetItem doesn't support setStyleSheet(), now uses setForeground() with QBrush/QColor
  - Fixed missing `no_journal_widget` attribute in ProfileScreen - widget now properly initialized in build_ui()
  - Fixed session sorting error with None values - added proper None handling in sort_key functions
- **Application Startup** - Improved startup reliability
  - Fixed potential crash during initial session scan
  - Added error handling around session manager initialization
  - Deferred heavy operations to prevent UI blocking
- Font initialization warnings (MS Sans Serif fallback issues)
- Initialization order issue with stacked widget

---

**Note:** This is an alpha release. The project is currently in active development. Version numbers and dates will be updated as releases are made.

