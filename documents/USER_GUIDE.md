# User Guide

**Author:** R.W. Harper  
**Last Updated:** 2026-02-12  
**License:** GPL-3.0

**Note (2026-02-12):** This version has not been fully tested.

## Prerequisites

Before using EDLA, ensure you have:

1. **Windows 10/11** (64-bit)
2. **Elite Dangerous installed** - The game must be installed and you must have played it at least once
   - Journal files are created when you play Elite Dangerous
   - Default location: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\` (can be overridden via config)
3. **Python 3.8+** (only if running from source, not needed for executable version)

### Optional: External configuration

Paths and optional keys are not embedded in the app. To override the default log or app-data directory (or to add an API key), copy `edla_config.sample.json` to `edla_config.json` in the application folder and edit it. Do not commit `edla_config.json`. See [CONFIG.md](CONFIG.md) for details.

## Getting Started

### First Launch

1. **Ensure Elite Dangerous journal files exist**
   - Play Elite Dangerous at least once to generate journal files
   - Journal files are created automatically when you start the game
   - Location: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

2. **Run the application** using `run.bat` or `python main.py` (or double-click `EDLA.exe` if using executable)

3. The application will automatically:
   - Scan your Elite Dangerous journal files
   - Detect commanders from journal files
   - Load existing profiles and session data
   - Start monitoring for new events

4. **Select a commander** from the "Select Commander" dropdown to start monitoring

5. **Expected Results:**
   - Monitor screen shows recent events (if any exist)
   - Dashboard shows session statistics
   - Profiles screen lists all detected commanders
   - If no journal files exist, informational messages guide you

### Understanding the Interface

#### Navigation Bar

The top navigation bar provides:
- **Commander**: Dropdown to select the active commander; use the refresh button (🔄) to rescan from journal files
- **Home Button**: Start page; when a commander is selected, shows welcome and startup snapshot (ranks, progress, powerplay, reputation). Refreshes when the Home tab is visible so new journal data appears.
- **Monitor Button**: Switch to the monitoring screen (highlighted when active)
- **Profiles Button**: Switch to the profiles management screen (highlighted when active)
- **Dashboard Button**: Switch to the session dashboard screen (highlighted when active)
- **Missions Button**: Switch to the Missions & Reputation view (active missions, completed/failed this session, reputation)
- **Help Menu**: Access About and License information

The window is resizable; panels scroll automatically when content does not fit.

#### Home Screen (startup snapshot)

When a commander is selected, the Home screen shows:

- **Last session start**: Ship, credits, star system, and game mode from the latest journal (LoadGame).
- **Ranks**: Combat, Trade, Exploration, CQC, Mercenary (Odyssey), Exobiologist (Odyssey), Federation Navy, Empire Navy — using in-game rank names (e.g. Baron, Pathfinder, Entrepreneur). Alliance is noted as reputation only.
- **Progress to next rank**: Percentage progress for each rank category.
- **Powerplay**: Power name, rank, merits, votes, time pledged (if pledged).
- **Superpower reputation**: Empire, Federation, Independent, Alliance (at session start).

Data is read from the latest journal file when you select a commander and is also updated live when new events (e.g. Rank, Progress) are written to the journal while the Home tab is visible. If no startup data is available yet, play and load into the game once, then select the commander again.

#### Monitor Screen

The Monitor screen is your main view for watching game events:

- **Commander Selection**: Use the Commander dropdown in the nav bar to choose which commander to monitor
- **Status Display**: Shows whether monitoring is active (should show "✓ Monitoring" when working)
- **Log Directory**: Displays where journal files are being read from
- **Recent Events**: Live list of events from Elite Dangerous (updates every second), with verbose one-line descriptions (e.g. jump details, station names, mission rewards)

**Expected Behavior:**
- Events appear within 1-2 seconds of occurring in Elite Dangerous
- Events are listed newest first (most recent at top)
- Shows up to 100 most recent events
- Updates automatically - no refresh needed
- If no journal files exist, shows informational message instead of event list
- If no events yet, shows "No events yet" message in gray text

#### Profiles Screen

The Profiles screen manages your commanders:

- **Existing Profiles**: List of all detected commanders
- **Refresh Button**: Rescans journal files to find new commanders
- **Manual Add**: Create a profile manually if needed

#### Missions & Reputation Screen

The Missions tab shows (for the current session):
- **Superpower Reputation Checkpoint Progress**: Faction reputation in a two-column table (Faction | Reputation). Data appears when the game sends a Reputation event (e.g. when you dock).
- **Completed Missions, Ready to Turn In**: Missions you have accepted, most recent first (name, faction, destination)
- **Completed This Session**: Missions completed this session with rewards
- **Failed / Abandoned This Session**: Missions failed or abandoned

If the reputation pane is empty, dock in-game once; the game sends reputation data at that time and it will show within a few seconds.

#### Dashboard Screen

The Dashboard screen provides historical session analysis:

- **Statistics Display**: Shows aggregated statistics:
  - Total Sessions
  - Total Jumps
  - Total Dockings
  - Total Events
  - First and Last Session dates
- **Session History**: List of all game sessions with:
  - Session start time
  - Commander name
  - Number of jumps
  - Number of events
- **Session Details**: Double-click any session to view:
  - Start and end times
  - Duration
  - Ships used (first and last)
  - Systems visited (first and last)
  - Jump count
  - Docking count
  - Total events
- **Commander Filtering**: When a commander is selected, only their sessions are shown
- **Refresh Button**: Manually rescan all log files for new sessions
- **Auto-Update**: Dashboard automatically refreshes when new sessions are detected

#### Help Menu

Access application information:
- **About EDLA**: View version, copyright, and license information
- **License**: View the full GPL-3.0 license text

### Common Tasks

#### Selecting a Commander

1. Use the Commander selection dropdown in the top navigation bar (or open it from the Home screen)
2. Choose your commander from the dropdown menu
3. Events will now be tracked for that commander; the status bar will briefly show "Revalidating logs…" then "Logs revalidated."

#### Refreshing Commander List

1. Go to the Profiles screen
2. Click "🔄 Refresh from Journal Files"
3. New commanders found in journals will be added automatically

#### Manually Adding a Profile

1. Go to the Profiles screen
2. Enter a commander name in the text field
3. Click "Add Profile"

#### Viewing Session History

1. Go to the Dashboard screen
2. Select a commander (optional - shows all sessions if none selected)
3. View statistics at the top
4. Browse session history in the list
5. Double-click any session to view detailed information

#### Refreshing Session Data

1. Go to the Dashboard screen
2. Click "🔄 Refresh Sessions" button
3. The application will scan all log files and update session data

## Understanding Events

### Event Types

Elite Dangerous generates many event types. Common ones include:

- **LoadGame**: When you start playing (contains commander name)
- **Docked**: When docking at a station
- **Undocked**: When leaving a station
- **FSDJump**: When jumping to another system
- **Location**: When entering a new location
- And many more...

### Event Display

Events are shown in the format:
```
[YYYY-MM-DDTHH:MM:SS] EventType
```

The most recent events appear at the top of the list.

## Profile Data

### Storage Location

Profiles are stored in:
```
%USERPROFILE%\.edla\profiles\
```

Each commander has a JSON file named `{CommanderName}.json`

Session data and processed-file tracking are stored in a SQLite database:
```
%USERPROFILE%\.edla\edla.db
```
No separate database install is required (SQLite is built into Python). If you had older `sessions.json` or `processed_files.json` files, they are imported once on first run and renamed to `.json.migrated`.

### Profile Contents

Each profile contains:
- Commander name and metadata
- Creation and last update timestamps
- Preferences (for future use)
- Statistics (event counts, last ship, last system, etc.)
- Tracked events (last 1000 events)

### Backup Recommendations

To backup your profiles and session data:
1. Copy the `.edla` folder from your user directory
2. Store it in a safe location
3. Restore by copying it back

This includes:
- All commander profiles (JSON files in `profiles\`)
- Session database (`edla.db`) — session history and processed-file tracking
- Application logs

## Troubleshooting

### No Commanders Detected

- Ensure Elite Dangerous journal files exist in:
  `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`
- Click "Refresh from Journal Files" to rescan
- Check that you've played Elite Dangerous at least once (to generate journal files)

### Events Not Appearing

- Ensure a commander is selected
- Check that monitoring status shows "✓ Monitoring"
- Verify the log directory path is correct
- Make sure Elite Dangerous is running and generating log files

### Application Won't Start

- Verify Python 3.8+ is installed
- Check that PyQt6 is installed: `pip install PyQt6`
- Ensure all dependencies are installed: `pip install -r requirements.txt`

## Tips and Best Practices

1. **Select Commander First**: Always select a commander before expecting events
2. **Regular Refreshes**: Refresh commander list after creating new Elite Dangerous accounts
3. **Profile Backups**: Regularly backup your `.edla` folder (includes profiles and session data)
4. **Multiple Commanders**: The app supports multiple commanders - switch between them as needed
5. **Active Screen Indicator**: The highlighted navigation button shows which screen you're currently viewing
6. **Dashboard Usage**: Use the Dashboard to view historical session data and statistics
7. **Session Tracking**: Sessions are automatically tracked - no manual setup required
8. **Help Menu**: Use Help → About to view version and copyright information
9. **Application Logs**: Check `logs/app.log` in the application directory if you encounter issues

## Getting Help

For issues, questions, or feature requests, please refer to:
- [TODO.md](../TODO.md) for planned features
- [CHANGELOG.md](../CHANGELOG.md) for version history
- [README.md](../README.md) for general information

