# How EDLA Works

**Author:** R.W. Harper  
**Last Updated:** 2026-02-12  
**License:** GPL-3.0

**Note (2026-02-12):** This version has not been fully tested.

## Overview

EDLA (Elite Dangerous Log Analyzer) is a desktop application that monitors, analyzes, and displays information from Elite Dangerous journal files in real-time. The application provides a comprehensive dashboard for tracking your gameplay statistics, session history, and commander profiles.

## Core Architecture

### 1. Log File Monitoring

**Location:** By default `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`. Can be overridden via `edla_config.json` (see [CONFIG.md](CONFIG.md)).

**How it works:**
- EDLA uses the `watchdog` library to monitor the Elite Dangerous log directory
- When Elite Dangerous creates or modifies `.log` files, EDLA detects the changes
- New lines in log files are parsed as JSON events
- Events are processed in real-time as they occur

**Expected Behavior:**
- The app automatically detects when Elite Dangerous is running
- Events appear in the Monitor screen within 1-2 seconds of occurring in-game
- No manual refresh needed - everything updates automatically

### 2. Event Processing Pipeline

```
Journal File → LogMonitor → EventTracker → ProfileManager → UI Update
```

**Components:**

1. **LogMonitor** (`log_monitor.py`)
   - Monitors file system for changes
   - Reads new lines from log files
   - Parses JSON events
   - Tracks file positions to avoid re-processing

2. **EventTracker** (`event_tracker.py`)
   - Processes individual events
   - Updates commander-specific statistics
   - Maintains recent events list (last 1000 events)
   - Filters events by selected commander

3. **ProfileManager** (`profile_manager.py`)
   - Manages commander profiles
   - Stores statistics per commander
   - Persists data to JSON files in `%USERPROFILE%\.edla\profiles\`
   - Auto-detects commanders from journal files

4. **SessionManager** (`session_manager.py`)
   - Identifies game sessions (from LoadGame events)
   - Tracks detailed session statistics
   - Stores session data and processed-file list in SQLite: `%USERPROFILE%\.edla\edla.db`
   - Migrates from legacy `sessions.json` / `processed_files.json` on first run if present
   - Processes historical log files on startup

5. **CurrentSessionTracker** (`current_session_tracker.py`)
   - Tracks the currently active game session
   - Updates statistics in real-time (including missions and reputation from MissionAccepted, MissionCompleted, MissionFailed, MissionAbandoned, Reputation events)
   - Provides live data for the Current Session dashboard view and the Missions & Reputation screen

### 3. Data Storage

**Profile Data:**
- Location: `%USERPROFILE%\.edla\profiles\{CommanderName}.json`
- Contains: Statistics, preferences, recent events, last known state

**Session Data and Processed-File Tracking:**
- Location: `%USERPROFILE%\.edla\edla.db` (SQLite database)
- Contains: All historical game sessions and the list of processed log files
- Uses Python’s built-in SQLite support; no separate database install
- If old `sessions.json` or `processed_files.json` exist, they are imported once and renamed to `.json.migrated`

**Application Logs:**
- Location: `logs/app.log` (in application directory)
- Contains: Application events, errors, debugging information

## User Interface Components

### Home Screen

**Purpose:** Start page, commander selection, and commander startup snapshot (ranks, progress, powerplay, reputation)

**How it works:**
- Default view when the application starts
- Shows “Select a commander first” when no commander is selected
- When a commander is selected: welcome plus snapshot (last session start, ranks with in-game names, progress %, powerplay, superpower reputation); data from journal startup reader and live Rank/Progress events; Home tab refreshes from tracker so new journal data appears without re-selecting commander
- Commander can be switched via the dropdown and refresh in the top navigation bar

**Expected Results:**
- App opens on Home; user can select a commander from the nav bar
- After selecting a commander, log revalidation runs in the background; status bar shows “Revalidating logs…” then “Logs revalidated.”

### Monitor Screen

**Purpose:** Real-time event monitoring

**How it works:**
- Displays recent events from the selected commander
- Updates every second automatically
- Shows event type, timestamp, and a verbose one-line description (e.g. FSDJump with system and distance, Docked with station name)
- List uses word wrap and tooltips; scrolls to top so newest events stay visible
- Displays monitoring status and log directory path

**Expected Results:**
- When Elite Dangerous is running, events appear in real-time
- Events are listed newest first (most recent at top)
- Shows up to 100 most recent events
- If no journal files exist, shows informational message
- If no events yet, shows "No events yet" message

### Profiles Screen

**Purpose:** Commander profile management

**How it works:**
- Automatically detects commanders from journal files
- Displays list of all known commanders
- Allows manual profile creation
- Refreshes commander list from journal files

**Expected Results:**
- Commanders are automatically detected when journal files exist
- Profile list shows all commanders found in journal files
- Double-clicking a profile selects that commander
- If no journal files exist, shows informational widget
- If journal files exist but no commanders found, shows helpful message

### Dashboard Screen

**Purpose:** Statistics and session history

**How it works:**
- Two view modes: Current Session and Historical
- Current Session: Real-time stats for active game session
- Historical: Aggregated stats across all past sessions
- Session list shows all sessions with key information
- Double-click sessions to view detailed information

**Expected Results:**

**Current Session View:**
- Shows live statistics while playing Elite Dangerous
- Updates automatically as events occur
- Displays: Credits, Money Earned/Spent, Light Years Traveled, Jumps, Systems/Stations/Planets Visited, Kills, Deaths, Combat stats
- Active Missions and Reputation (faction reputation) from the current session
- If no active session, shows "No active session" message

**Historical View:**
- Shows aggregated statistics across all sessions
- Organized in tabs: Overview, Combat, Exploration, Trading, Missions
- Session list shows: Date, Commander, Jumps, Systems, Credits Change, Events
- Double-clicking a session shows detailed breakdown
- If no sessions exist, shows "No sessions found" message

### Missions & Reputation Screen

**Purpose:** Current-session missions and faction reputation

**How it works:**
- Dedicated view for active missions, completed/failed this session, and faction reputation
- Data comes from the current session tracker (MissionAccepted, MissionCompleted, MissionFailed, MissionAbandoned, Reputation events)
- Updates in real time as events are processed

**Expected Results:**
- Active missions list shows name, faction, destination
- Completed and failed/abandoned sections show missions from the current session only
- Reputation reflects current faction standings (from the journal `Reputation` event; the game sends this when you dock or at certain events, so the pane may be empty until then)

## Expected Workflow

### First Time Setup

1. **Install Elite Dangerous** (if not already installed)
2. **Play Elite Dangerous at least once** to generate journal files
3. **Launch EDLA** using `run.bat`
4. **Select a Commander** from the dropdown menu
5. **View Events** in the Monitor screen
6. **Check Dashboard** for session statistics

### Normal Usage

1. **Launch EDLA** (can be before or after starting Elite Dangerous)
2. **Select Commander** if you have multiple commanders
3. **Monitor Screen:**
   - Watch events appear in real-time as you play
   - Events update automatically every second
4. **Dashboard Screen:**
   - Switch to "Current Session" to see live stats
   - Switch to "Historical" to see all-time stats
   - View detailed session information by double-clicking
5. **Profiles Screen:**
   - View all detected commanders
   - Manually add profiles if needed
   - Refresh from journal files if new commanders appear

## Data Flow Example

### Example: Player Jumps to a New System

1. **In Elite Dangerous:**
   - Player performs FSD jump
   - Elite Dangerous writes `FSDJump` event to journal file

2. **EDLA Detection (within 1-2 seconds):**
   - `LogMonitor` detects file modification
   - Reads new line from journal file
   - Parses JSON event

3. **Event Processing:**
   - `EventTracker` receives event
   - Updates commander statistics (jumps count, systems visited)
   - Adds to recent events list
   - `CurrentSessionTracker` updates session stats (light years, jumps, systems)
   - `SessionManager` updates current session data

4. **UI Update:**
   - Monitor screen shows new event in list
   - Dashboard Current Session view updates statistics
   - All updates happen automatically

## Key Features Explained

### Automatic Commander Detection

**How it works:**
- Scans journal files for `LoadGame` events
- Extracts `Commander` field from events
- Creates profiles automatically
- Profiles persist between sessions

**Expected Results:**
- Commanders appear in dropdown menu automatically
- No manual setup required
- Multiple commanders supported
- Each commander has separate statistics

### Session Tracking

**How it works:**
- Identifies sessions by `LoadGame` events
- Tracks session from LoadGame to next LoadGame or app shutdown
- Calculates statistics for each session
- Stores session data persistently

**Expected Results:**
- Each game session is tracked separately
- Session statistics include: credits, jumps, systems, combat, exploration, trading, missions
- Historical sessions are preserved
- Can view detailed breakdown of any session

### Real-Time Updates

**How it works:**
- File system monitoring detects changes immediately
- UI updates every 2 seconds via QTimer (reduces CPU and keeps the app responsive)
- Missions & Reputation screen only rebuilds when its data actually changes
- No manual refresh needed

**Expected Results:**
- Events appear within 1–2 seconds of occurring
- Dashboard statistics update automatically
- Current session stats reflect live gameplay
- Smooth, responsive user experience

## Error Handling

### No Journal Files

**Expected Behavior:**
- Informational widget appears on all screens
- Explains that journal files are needed
- Provides instructions on how to get started
- No errors or crashes

### Missing Dependencies

**Expected Behavior:**
- Batch file checks for PyQt6 and watchdog
- Automatically installs if missing
- Logs installation process
- Application starts after dependencies installed

### Application Crashes

**Expected Behavior:**
- Error logged to `logs/app.log`
- Batch file logs to `logs/run_YYYYMMDD_HHMMSS.log`
- Error details in `logs/error.log`
- User can review logs to diagnose issues

## Performance Characteristics

### Startup Time

- **Expected:** 2-5 seconds
- Initial log scan may take longer with many log files
- UI appears immediately, scanning happens in background

### Memory Usage

- **Expected:** 50-200 MB depending on data size
- Profiles and sessions stored in memory
- Recent events limited to 1000 items

### CPU Usage

- **Expected:** < 5% when idle
- Slight increase during active gameplay
- File monitoring is efficient

### Disk I/O

- **Expected:** Minimal
- Only writes when data changes
- Reads log files incrementally (only new lines)

## Troubleshooting

### Events Not Appearing

**Check:**
1. Elite Dangerous is running and generating journal files
2. Correct commander is selected
3. Log directory path is correct
4. Journal files exist in expected location

### Statistics Not Updating

**Check:**
1. Current session is active (Elite Dangerous running)
2. Correct view mode selected (Current Session vs Historical)
3. Commander is selected
4. Application logs for errors

### Sessions Not Showing

**Check:**
1. Journal files contain LoadGame events
2. Sessions have been processed (check logs)
3. Correct commander selected (if filtering)
4. Refresh sessions button clicked

### Reputation Pane Empty

**Check:**
1. Commander is selected and you have an active session (game has been run this session).
2. The game sends a `Reputation` event when you dock or at certain other times; the pane only shows data after such an event.
3. If you have just started the app, dock in-game once and the reputation data should appear on the next refresh (within a few seconds).

## Technical Details

### Threading

- Log monitoring runs in separate thread (QThread)
- UI updates on main thread
- Thread-safe event passing via signals

### Data Persistence

- **Profiles:** JSON files in `%USERPROFILE%\.edla\profiles\`; atomic writes (write to temp file, then rename)
- **Sessions and processed files:** SQLite database (`edla.db`); no large JSON files
- **Error recovery:** Corrupted profile or legacy JSON is handled gracefully (exceptions caught, optional backup); app does not crash on invalid JSON

### File Monitoring

- Uses `watchdog` library
- Efficient file system event detection
- Handles file creation and modification
- Tracks file positions to avoid re-reading

## Future Enhancements

See `TODO.md` for planned features and improvements.

