# TODO

**Author:** R.W. Harper  
**Last Updated:** 2025-12-22  
**License:** GPL-3.0

This file tracks planned features, improvements, and tasks for the Elite Dangerous Log Analyzer.

## High Priority

- [ ] Expand event tracking to capture more game events
- [ ] Add event filtering capabilities
- [ ] Implement event search functionality
- [x] Session tracking: start/stop sessions, compute profit per session (Basic session tracking implemented - tracks sessions from log files)
- [ ] Track Powerplay merits earned per session and cumulatively
- [ ] Track ranks (combat/trade/exploration/exobiology/power) with deltas
- [ ] Track combat stats (kills, deaths, bounties, bonds) with session totals
- [ ] Track exobiology stats (samples, species, payouts) with session totals
- [ ] Track exploration stats (jumps, scans, FSS finds, credits) with session totals
- [ ] Add export/import functionality for profiles
- [ ] Create statistics dashboard/visualization
- [ ] Add customizable notifications for specific events

## Medium Priority

- [ ] Add event details view (click on event to see full JSON)
- [ ] Implement event history browsing (beyond recent 1000 events)
- [ ] Add commander statistics comparison view
- [ ] Create event timeline visualization
- [ ] Add configuration options for log directory path
- [ ] Implement profile backup/restore functionality
- [ ] Add dark/light theme toggle
- [ ] Create settings/preferences screen
- [ ] Session timelines with charts (profit, merits, exploration, combat)
- [x] Data visualization dashboard (charts for ranks, credits, merits, kills, scans) (Basic dashboard implemented - shows session statistics and history)
- [ ] Export session summaries to CSV/JSON

## Build and Distribution

- [ ] Create application icon (app.ico) for Windows executable
- [ ] Test PyInstaller build process
- [ ] Create final Inno Setup installer script
- [ ] Test installer on clean Windows system
- [ ] Create distribution package (zip with installer)
- [ ] Set up automated build process
- [ ] Code signing for Windows executable (optional)

## Low Priority

- [ ] Add unit tests
- [ ] Add integration tests
- [ ] Create user documentation
- [ ] Add keyboard shortcuts
- [ ] Implement event categories/tags
- [ ] Add event export to CSV/JSON
- [ ] Create command-line interface option
- [ ] Add logging/debugging features
- [ ] Performance optimizations for large log files

## Future Considerations

- [ ] Multi-platform support (Linux, macOS)
- [ ] Plugin system for custom event handlers
- [ ] Integration with Elite Dangerous API (if available)
- [ ] Cloud sync for profiles
- [ ] Mobile companion app
- [ ] Web interface option

## Known Issues

- None currently documented

---

**Note:** This TODO list is subject to change as the project evolves. Items may be added, removed, or reprioritized based on user feedback and development priorities.

