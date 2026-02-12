# Developer Guide

**Author:** R.W. Harper  
**Last Updated:** 2026-02-12  
**License:** GPL-3.0

**Note (2026-02-12):** This version has not been fully tested.

## Prerequisites

- Python 3.8 or higher
- PyQt6 development libraries
- Basic understanding of Python and GUI development
- Familiarity with Elite Dangerous journal file format

## Development Setup

### Initial Setup

1. Clone or download the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate.bat
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Data Storage

Session and processed-file data use **SQLite** (`%USERPROFILE%\.edla\edla.db`). The `sqlite3` module is part of the Python standard library, so no extra dependency is required. Commander profiles remain in JSON files under `profiles\`.

### Development Dependencies

For development, you may want to install additional tools:

```bash
pip install black flake8 mypy pytest
```

## Code Structure

### Module Responsibilities

- **main.py**: GUI application, UI components (Home, Monitor, Profiles, Dashboard, Missions), event handling, commander bar, log revalidation
- **config.py**: Configuration and path management; loads optional `edla_config.json` from the application directory (paths, optional API keys). Do not commit `edla_config.json`; use `edla_config.sample.json` as a template. See [CONFIG.md](CONFIG.md).
- **profile_manager.py**: Profile CRUD operations and persistence (JSON)
- **log_monitor.py**: File system monitoring and log parsing
- **event_tracker.py**: Event processing and statistics
- **commander_detector.py**: Commander detection from journal files
- **session_manager.py**: Session tracking and analysis from log files; persists sessions and processed-file list in SQLite (`edla.db`)
- **dashboard_screen.py**: Dashboard UI component for session visualization
- **missions_reputation_screen.py**: Missions & Reputation UI (missions ready to turn in, completed/failed this session, Superpower Reputation pane). Refreshes only when mission/reputation data actually changes to avoid sluggishness.
- **journal_aux_reader.py**: Reads auxiliary journal JSON (Cargo.json, NavRoute.json, Market.json) from the journal directory
- **journal_startup_reader.py**: Reads the latest journal file and extracts startup sequence (LoadGame, Rank, Progress, Powerplay, Reputation) for the Home screen snapshot
- **current_session_tracker.py**: Real-time session statistics and mission/reputation tracking (MissionAccepted, MissionCompleted, MissionFailed, MissionAbandoned, Reputation events). Reputation event supports both flat key-value and a `Factions` array; text levels (Friendly, Allied, etc.) are mapped to 0–100. Feeds Dashboard Current Session and Missions & Reputation screen.
- **no_journal_widget.py**: Reusable “no journal files” informational widget

### Adding New Features

#### Adding a New Event Handler

1. Modify `event_tracker.py`:
   ```python
   def update_stats_from_event(self, profile, event_data):
       event_type = event_data.get("event", "")
       # Add your event handling here
       if event_type == "YourEvent":
           # Process event
   ```

#### Adding a New UI Screen

1. Create a new QWidget class (can be in `main.py` or in a separate file such as `dashboard_screen.py` or `missions_reputation_screen.py`)
2. Add it to the stacked widget:
   ```python
   self.stacked_widget.addWidget(your_new_screen)
   ```
3. Add navigation button in the nav bar
4. Update `update_nav_button_styles()` to handle the new screen index

#### Adding Configuration Options

1. Add constants to `config.py`
2. Update `CommanderProfile` to store preferences
3. Add UI controls in appropriate screen

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Document functions and classes with docstrings
- Keep functions focused and single-purpose
- Use meaningful variable and function names

## Testing

### Running Tests

Currently, no test suite is implemented. Future testing should include:

- Unit tests for each module
- Integration tests for component interactions
- UI tests for user interactions

### Manual Testing Checklist

- [ ] Application starts without errors
- [ ] Commanders are detected from journal files
- [ ] Events are tracked correctly
- [ ] Profile creation works
- [ ] UI updates properly
- [ ] Dashboard displays session statistics
- [ ] Session history is populated correctly
- [ ] Session details dialog works
- [ ] Commander filtering works on dashboard
- [ ] New log files are processed automatically
- [ ] No memory leaks during extended use

## Debugging

### Application Logging

EDLA includes built-in logging that writes to:
```
logs/app.log
```
(Relative to the application directory)

Logs include:
- Application startup/shutdown
- Commander detection
- Event processing
- Error messages

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **PyQt6 Errors**: Verify PyQt6 is installed correctly
3. **File Permission Errors**: Check write permissions for profile directory
4. **Log Parsing Errors**: Verify journal file format matches expected JSON
5. **Font Warnings**: These are harmless - application uses system default fonts

### Debug Mode

The application already has logging enabled. To increase verbosity, modify `main.py`:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    ...
)
```

## Building and Distribution

### Prerequisites

1. **PyInstaller** - For creating Windows executables
   ```bash
   pip install pyinstaller
   ```

2. **Inno Setup** (optional) - For creating Windows installers
   - Download from: https://jrsoftware.org/isdl.php
   - Add to PATH or update build script with full path

### Creating Executable

The project includes a PyInstaller spec file (`EDLA.spec`) and build script (`build_exe.bat`).

**Quick Build:**
```bash
build_exe.bat
```

**Manual Build:**
```bash
pyinstaller EDLA.spec
```

The executable will be created in `dist/EDLA.exe`

**Important Notes:**
- The spec file includes all necessary PyQt6 imports
- Documentation and assets are automatically included
- Console is disabled (GUI-only application)
- Icon will be used if `assets/app.ico` exists

### Creating Installer

After building the executable, create an installer:

**Using Inno Setup:**
1. Install Inno Setup from https://jrsoftware.org/isdl.php
2. Update `installer_script.iss` with your AppId
3. Run: `build_installer.bat`

**Manual Build:**
```bash
iscc installer_script.iss
```

The installer will be created in `Output/EDLA_Setup.exe`

### Build Configuration

**EDLA.spec** - PyInstaller configuration:
- Includes `documents/` folder
- Includes `assets/` folder
- Sets console=False (no console window)
- Uses icon from `assets/app.ico` if available

**installer_script.iss** - Inno Setup configuration:
- Creates desktop shortcut (optional)
- Includes documentation
- Sets up uninstaller
- Uses GPL-3.0 license file

### Testing the Build

1. **Test Executable:**
   - Run `dist/EDLA.exe` directly
   - Verify all features work
   - Check that profiles are created in user directory
   - Check that logs are created in application directory

2. **Test Installer:**
   - Install on clean Windows system
   - Verify installation location
   - Test uninstaller
   - Verify shortcuts work

### Distribution Checklist

- [ ] Application icon created (`assets/app.ico`)
- [ ] Executable builds successfully
- [ ] Executable runs without errors
- [ ] All features work in executable
- [ ] Installer builds successfully
- [ ] Installer tested on clean system
- [ ] License file included
- [ ] Documentation included
- [ ] Version number updated in all files

## Contributing

### Code Contribution Process

1. Create a feature branch
2. Make changes following code style
3. Test thoroughly
4. Update documentation as needed
5. Submit for review

### Documentation Updates

When adding features:
- Update README.md if user-facing
- Update USER_GUIDE.md for user features
- Update ARCHITECTURE.md for structural changes
- Update CHANGELOG.md with date and changes
- Update TODO.md for completed items
- Update DEVELOPER_GUIDE.md for developer-facing changes

## Elite Dangerous Journal Format

Journal files are JSON-formatted, one event per line. Key events:

- **FileHeader**: First line, contains metadata
- **LoadGame**: Contains Commander name
- **Docked**, **Undocked**: Station events
- **FSDJump**: System jumps
- **Location**: Location changes

See `documents/JOURNAL_FORMAT.md` for more details.

## Future Development Areas

- Plugin system architecture
- Database backend option
- API layer design
- Performance optimizations
- Multi-platform support

## Resources

- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Elite Dangerous Journal Documentation](https://elite-journal.readthedocs.io/)
- [Python Style Guide (PEP 8)](https://pep8.org/)

