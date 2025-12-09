# Changelog

**Author:** R.W. Harper  
**Last Updated:** 2025-12-09  
**License:** GPL-3.0

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - Alpha 1.0

### Added
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
- Application logging system
- Build infrastructure for Windows executables (PyInstaller)
- Inno Setup installer script template
- Comprehensive documentation (User Guide, Developer Guide, Build Guide, Architecture, Journal Format)

### Changed
- Migrated from Kivy/KivyMD to PyQt6 for better Windows compatibility
- Improved Select Commander button visibility (brighter color, white border)
- Fixed font warnings by using system default fonts
- Enhanced UI with active state indicators for navigation buttons

### Fixed
- Font initialization warnings (MS Sans Serif fallback issues)
- Initialization order issue with stacked widget

---

**Note:** This is an alpha release. The project is currently in active development. Version numbers and dates will be updated as releases are made.

