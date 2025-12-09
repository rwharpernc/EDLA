# User Guide

**Author:** R.W. Harper  
**Last Updated:** 2025-12-09  
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

2. **Run the application** using `run.bat` or `python main.py` (or double-click `EDLA.exe` if using executable)

3. The application will automatically scan your Elite Dangerous journal files

4. Commanders found in journal files will be automatically added as profiles

5. Select a commander from the "Select Commander" dropdown to start monitoring

### Understanding the Interface

#### Navigation Bar

The top navigation bar provides:
- **Select Commander Button**: Choose which commander to monitor (highlighted with white border)
- **Monitor Button**: Switch to the monitoring screen (highlighted when active)
- **Profiles Button**: Switch to the profiles management screen (highlighted when active)
- **Help Menu**: Access About and License information

#### Monitor Screen

The Monitor screen is your main view for watching game events:

- **Commander Selection**: Click "Select Commander" to choose which commander to monitor
- **Status Display**: Shows whether monitoring is active
- **Log Directory**: Displays where journal files are being read from
- **Recent Events**: Live list of events from Elite Dangerous (updates every second)

#### Profiles Screen

The Profiles screen manages your commanders:

- **Existing Profiles**: List of all detected commanders
- **Refresh Button**: Rescans journal files to find new commanders
- **Manual Add**: Create a profile manually if needed

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

### Profile Contents

Each profile contains:
- Commander name and metadata
- Creation and last update timestamps
- Preferences (for future use)
- Statistics (event counts, last ship, last system, etc.)
- Tracked events (last 1000 events)

### Backup Recommendations

To backup your profiles:
1. Copy the `.edla` folder from your user directory
2. Store it in a safe location
3. Restore by copying it back

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
3. **Profile Backups**: Regularly backup your `.edla` folder
4. **Multiple Commanders**: The app supports multiple commanders - switch between them as needed
5. **Active Screen Indicator**: The highlighted navigation button shows which screen you're currently viewing
6. **Help Menu**: Use Help → About to view version and copyright information
7. **Application Logs**: Check `%USERPROFILE%\.edla\logs\app.log` if you encounter issues

## Getting Help

For issues, questions, or feature requests, please refer to:
- [TODO.md](../TODO.md) for planned features
- [CHANGELOG.md](../CHANGELOG.md) for version history
- [README.md](../README.md) for general information

