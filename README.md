# Elite Dangerous Log Analyzer (EDLA)

**Author:** R.W. Harper  
**Last Updated:** 2025-12-09  
**License:** GPL-3.0  
**Version:** Alpha 1.0 (Unreleased - Early Prototype)

> **⚠️ WARNING: This is an early prototype and is NOT for public use or testing. The project is in active development and many features are incomplete or not yet implemented.**

> **Note:** EDLA is a temporary project name and may change as the project evolves.

A Python GUI application (early prototype) for monitoring and analyzing Elite Dangerous log files in real-time. Currently supports basic commander profile management and event tracking. Many planned features are not yet implemented.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Documentation](#documentation)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Current Status

**⚠️ Early Prototype - Not for Public Use**

This is a very early prototype with basic functionality. The application currently provides:
- Basic UI framework with dark theme
- Commander detection from journal files
- Simple event display
- Basic profile management

**Many planned features are not yet implemented.** See [TODO.md](TODO.md) for planned functionality.

## Current Features (Alpha 1.0)

- **Basic UI Framework** - PyQt6-based dark-themed interface
- **Commander Detection** - Automatically scans journal files for commanders
- **Basic Event Display** - Shows recent events from journal files
- **Simple Profile Management** - Create and manage commander profiles
- **Navigation System** - Switch between Monitor and Profiles screens
- **Help Menu** - About and License dialogs

## System Requirements

### Required Software

- **Windows 10/11** (64-bit)
- **Elite Dangerous** - The game must be installed and run at least once to generate journal files
  - Journal files are located at: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`
  - The game does not need to be running while using EDLA, but journal files must exist

### For Development/Manual Installation

If you're running from source code (not using a pre-built executable):

- **Python 3.8 or higher** (Python 3.14 supported)
  - Download from: https://www.python.org/downloads/
  - Ensure "Add Python to PATH" is checked during installation

### Optional

- **Virtual environment** (recommended for development)
  - Created automatically by `setup.bat`
  - Or manually: `python -m venv venv`

## Installation

**⚠️ This is a development prototype. Executable builds are not yet available.**

### For Developers (Source Code Only)

#### Option 1: Using Virtual Environment (Recommended)

1. **Ensure Python 3.8+ is installed** (download from python.org)

2. Run the setup script:
   ```bash
   setup.bat
   ```

   This will:
   - Create a virtual environment
   - Install all dependencies
   - Set everything up automatically

3. Run the application:
   ```bash
   run.bat
   ```

   Or manually:
   ```bash
   venv\Scripts\activate.bat
   python main.py
   ```

#### Option 2: Global Installation

1. Install dependencies directly:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python main.py
   ```

**Note:** Using a virtual environment is recommended to avoid conflicts with other Python projects.

## Quick Start (For Developers Only)

**⚠️ This is a development prototype. Not intended for end users.**

1. **Ensure Elite Dangerous journal files exist**
   - Play Elite Dangerous at least once to generate journal files
   - Files are located at: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

2. **Launch the application**
   - Source: Run `run.bat` or `python main.py`
   - (Executable builds not yet available)

3. **Select a commander** from the "Select Commander" dropdown
   - Commanders are automatically detected from journal files

4. **View events** - Basic event display shows recent events from journal files

5. **Manage profiles** - Basic profile management available in Profiles screen

## Current Functionality (Alpha 1.0)

### Monitor Screen

Basic monitoring interface:
- Commander selection
- Monitoring status display
- Log directory path
- Simple event list (basic display only)

### Profiles Screen

Basic profile management:
- View detected commanders
- Refresh commander list from journal files
- Manually add profiles

**Note:** Many planned features are not yet implemented. This is a minimal prototype.

### Log File Location

The application monitors log files from:
```
%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\
```

### Profile Data Storage

Profile data is stored in:
```
%USERPROFILE%\.edla\profiles\
```

Each commander has their own JSON profile file containing:
- Commander name and metadata
- Preferences
- Statistics (event counts, last ship, last system, etc.)
- Tracked events (last 1000 events)

## Documentation

Comprehensive documentation is available in the `documents/` folder:

- **[User Guide](documents/USER_GUIDE.md)** - Complete user documentation with troubleshooting
- **[Developer Guide](documents/DEVELOPER_GUIDE.md)** - Information for developers and contributors
- **[Build Guide](documents/BUILD_GUIDE.md)** - Instructions for building executables and installers
- **[Architecture Documentation](documents/ARCHITECTURE.md)** - Project structure and design
- **[Journal Format Guide](documents/JOURNAL_FORMAT.md)** - Elite Dangerous journal file format reference

### Additional Documentation

- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes
- **[TODO.md](TODO.md)** - Planned features and improvements

## Project Structure

```
EDLA/
├── main.py                 # Main application entry point
├── config.py               # Configuration and paths
├── profile_manager.py      # Profile management
├── log_monitor.py          # Log file monitoring
├── event_tracker.py        # Event tracking
├── commander_detector.py  # Commander detection
├── requirements.txt        # Python dependencies
├── documents/              # Documentation folder
│   ├── USER_GUIDE.md
│   ├── DEVELOPER_GUIDE.md
│   ├── ARCHITECTURE.md
│   └── JOURNAL_FORMAT.md
├── CHANGELOG.md           # Version history
├── TODO.md                 # Project tasks
└── README.md              # This file
```

## Development Status

**This project is in early development and is not ready for public use or testing.**

For developers interested in the codebase:
- See [Developer Guide](documents/DEVELOPER_GUIDE.md) for setup instructions
- Check [TODO.md](TODO.md) for planned features
- Review [Architecture Documentation](documents/ARCHITECTURE.md) for code structure

**Note:** This is a personal project in active development. Many features are incomplete.

## Troubleshooting

### No Commanders Detected

- **Elite Dangerous not installed**: Install Elite Dangerous and play it at least once
- **Journal files missing**: Ensure journal files exist at:
  `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`
- **No LoadGame events**: Play the game and load a save to generate LoadGame events
- Click "Refresh from Journal Files" to rescan

### Events Not Appearing

- Ensure a commander is selected
- Check that monitoring status shows "✓ Monitoring"
- Verify the log directory path is correct
- Make sure Elite Dangerous is running and generating new events

### Application Won't Start

**For executable version:**
- Ensure Windows 10/11 (64-bit)
- Check Windows Event Viewer for error details
- Verify Elite Dangerous is installed

**For source code version:**
- Verify Python 3.8+ is installed: `python --version`
- Check that PyQt6 is installed: `pip install PyQt6`
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Activate virtual environment if using one: `venv\Scripts\activate.bat`

For more detailed troubleshooting, see the [User Guide](documents/USER_GUIDE.md).

## Planned Features

**⚠️ Most features are planned but not yet implemented.**

See [TODO.md](TODO.md) for a complete list of planned features, including:
- Session tracking (profit, merits, ranks)
- Combat, exploration, and exobiology statistics
- Data visualization and charts
- Advanced event filtering and search
- Export/import functionality
- Customizable notifications
- And much more...

**This is an early prototype. Most functionality is still in development.**

## License

This project is provided as-is for personal use.

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).

Copyright © 2025 R.W. Harper

See the [LICENSE](LICENSE) file for the full license text, or view it in the application via Help → License.

## Acknowledgments

- Built with [PyQt6](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- Uses [watchdog](https://github.com/gorakhargosh/watchdog) for file monitoring
- Inspired by the Elite Dangerous community

---

**Author:** R.W. Harper  
**Project Name:** EDLA (temporary - subject to change)  
**Version:** Alpha 1.0 (Unreleased)
