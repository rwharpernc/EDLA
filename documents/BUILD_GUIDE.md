# Build Guide

**Author:** R.W. Harper  
**Last Updated:** 2026-02-12  
**License:** GPL-3.0

**Note (2026-02-12):** This version has not been fully tested.

This guide explains how to build EDLA as a Windows executable and create an installer.

## Prerequisites

### Required

- Python 3.8 or higher
- Virtual environment with dependencies installed
- PyInstaller (will be installed automatically by build script)

### Optional (for installer)

- Inno Setup 6 or higher
  - Download from: https://jrsoftware.org/isdl.php
  - Add to system PATH or update build script

## Building the Executable

### Quick Build

1. Ensure virtual environment is set up:
   ```bash
   setup.bat
   ```

2. Run the build script:
   ```bash
   build_exe.bat
   ```

3. The executable will be in `dist/EDLA.exe`

### Manual Build

1. Activate virtual environment:
   ```bash
   venv\Scripts\activate.bat
   ```

2. Install PyInstaller (if not already installed):
   ```bash
   pip install pyinstaller
   ```

3. Build using the spec file:
   ```bash
   pyinstaller EDLA.spec
   ```

### Build Output

- **dist/EDLA.exe** - The standalone executable
- **build/** - Temporary build files (can be deleted)
- **EDLA.spec** - PyInstaller configuration file

### Testing the Executable

1. Run the executable:
   ```bash
   dist\EDLA.exe
   ```

2. Verify:
   - Application starts without errors
   - All features work correctly
   - Profiles are created in user directory (`%USERPROFILE%\.edla\profiles\`)
   - Session database is created (`%USERPROFILE%\.edla\edla.db`) — SQLite, no extra install
   - Logs are written to user directory
   - No console window appears (GUI-only)

## Creating the Installer

### Prerequisites

1. Build the executable first (see above)
2. Install Inno Setup from https://jrsoftware.org/isdl.php
3. Ensure `installer_script.iss` exists

### Quick Build

```bash
build_installer.bat
```

### Manual Build

1. Open Inno Setup Compiler
2. Load `installer_script.iss`
3. Click "Build" → "Compile"

Or use command line:
```bash
iscc installer_script.iss
```

### Installer Output

- **Output/EDLA_Setup.exe** - The installer executable

### Installer Features

- Installs to Program Files
- Creates Start Menu shortcut
- Optional desktop shortcut
- Includes uninstaller
- Includes documentation
- Includes license file

## Configuration Files

### EDLA.spec

PyInstaller specification file that defines:
- Entry point (main.py)
- Included data files (documents, assets)
- Hidden imports (PyQt6 modules)
- Executable settings (no console, icon, etc.)

**Key Settings:**
- `console=False` - No console window
- `icon='assets/app.ico'` - Application icon (if exists)
- `datas` - Includes documents and assets folders

### installer_script.iss

Inno Setup script that defines:
- Application name and version
- Installation directory
- Files to include
- Shortcuts to create
- License file

**Important:** Update `AppId` in the script before building!

## Application Icon

To add an icon to the executable:

1. Create or obtain an ICO file (256x256 recommended)
2. Place it in `assets/app.ico`
3. Rebuild the executable

The icon will automatically be used in:
- The executable file
- The installer
- Windows shortcuts

## Troubleshooting

### Build Fails

- **Missing dependencies**: Run `pip install -r requirements.txt`
- **PyInstaller not found**: Run `pip install pyinstaller`
- **Import errors**: Check that all modules are in requirements.txt

### Executable Doesn't Run

- **Missing DLLs**: PyInstaller should bundle everything, but check PyQt6 installation
- **Path issues**: Verify paths work for frozen executables. Use `edla_config.json` (copy from `edla_config.sample.json`) next to the executable to override log or app-data paths; do not commit `edla_config.json`. See [CONFIG.md](CONFIG.md).
- **Logging errors**: Check that LOGS_DIR is writable

### Installer Issues

- **Inno Setup not found**: Install Inno Setup and add to PATH
- **Missing files**: Verify all files referenced in .iss exist
- **AppId error**: Update AppId in installer_script.iss

## Distribution Checklist

Before distributing:

- [ ] Version number updated in config.py
- [ ] Version number updated in installer script
- [ ] Application icon created and included
- [ ] Executable tested on clean system
- [ ] Installer tested on clean system
- [ ] License file included
- [ ] Documentation included
- [ ] All features work in executable
- [ ] No console window appears
- [ ] Logs write to correct location
- [ ] Profiles save correctly
- [ ] Session database (edla.db) is created and used in app data directory
- [ ] Repo is clean for distribution: no `edla_config.json`, `.edla/`, `logs/`, `build/`, or `dist/` committed (see [CONFIG.md](CONFIG.md)).

## File Sizes

Typical sizes:
- **EDLA.exe**: ~50-100 MB (includes PyQt6 and dependencies)
- **EDLA_Setup.exe**: ~50-100 MB (compressed installer)

## Future Enhancements

- Code signing for Windows
- Automated build process
- Multi-version builds
- Update mechanism
- Portable version option

