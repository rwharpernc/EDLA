# User Guide

**Author:** R.W. Harper  
**Last Updated:** 2025-12-22  
**License:** GPL-3.0

## Prerequisites

Before using EDLA, ensure you have:

1. **Windows 10/11** (64-bit)
2. **Elite Dangerous installed** - The game must be installed and you must have played it at least once
   - Journal files are created when you play Elite Dangerous
   - Location: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`
3. **Python 3.8+** (only if running from source, not needed for executable version)

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
- **Select Commander Button**: Choose which commander to monitor (highlighted with white border)
- **Monitor Button**: Switch to the monitoring screen (highlighted when active)
- **Profiles Button**: Switch to the profiles management screen (highlighted when active)
- **Dashboard Button**: Switch to the session dashboard screen (highlighted when active)
- **Help Menu**: Access About and License information

#### Monitor Screen

The Monitor screen is your main view for watching game events:

- **Commander Selection**: Click "Select Commander" to choose which commander to monitor
- **Status Display**: Shows whether monitoring is active (should show "✓ Monitoring" when working)
- **Log Directory**: Displays where journal files are being read from
- **Recent Events**: Live list of events from Elite Dangerous (updates every second)

**Expected Behavior:**
- Events appear within 1-2 seconds of occurring in Elite Dangerous
- Events are listed newest first (most recent at top)
- Shows up to 50 most recent events
- Updates automatically - no refresh needed
- If no journal files exist, shows informational message instead of event list
- If no events yet, shows "No events yet" message in gray text

#### Profiles Screen

The Profiles screen manages your commanders:

- **Existing Profiles**: List of all detected commanders
- **Refresh Button**: Rescans journal files to find new commanders
- **Manual Add**: Create a profile manually if needed

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

1. Click "Select Commander" in the top navigation bar
2. Choose your commander from the dropdown menu
3. Events will now be tracked for that commander

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

Session data is stored in:
```
%USERPROFILE%\.edla\sessions.json
```

Processed file tracking is stored in:
```
%USERPROFILE%\.edla\processed_files.json
```

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
- All commander profiles
- Session history data
- Processed file tracking
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

