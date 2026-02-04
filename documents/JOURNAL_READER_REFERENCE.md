# EliteJournalReader Reference & EDLA Porting Notes

**Author:** R.W. Harper  
**Last Updated:** 2025-02-04  
**License:** GPL-3.0

This document summarizes two related C# projects and what EDLA has ported or may use:

- **[EliteJournalReader](https://github.com/WarmedxMints/EliteJournalReader)** – Journal parsing library (events, Cargo/NavRoute/Market).
- **[ODEliteTracker](https://github.com/WarmedxMints/ODEliteTracker)** – Full tracker app for missions, BGS, Powerplay, mining, fleet carriers, and colonisation.

## About EliteJournalReader

- **Repo:** https://github.com/WarmedxMints/EliteJournalReader  
- **Language:** C#  
- **Purpose:** Read Elite: Dangerous journal feed from files; expose events via .NET events.  
- **License:** MIT  
- **Reference:** [Journal Manual v18](http://hosting.zaonce.net/community/journal/v18/Journal_Manual_v18.pdf) (Frontier).

### Architecture (C#)

- **JournalWatcher** – Extends `FileSystemWatcher`; watches the Elite Dangerous Save Games folder.
  - Filter: `Journal*.*.log`
  - **ProcessPreviousJournals()** – Replays current play session from existing journal files before going “live.”
  - **ParseHistory()** – Optional full history parse (e.g. for rebuild).
  - Uses **file offset** to read only new data from the current journal file.
  - **Polling** – Every 5 s checks for a new journal file (in case the file watcher misses creation).
  - **IsLive** – True after replay is done and watcher is reading new lines.
- **Event system** – One C# class per event type in `EliteJournalReader.Events` (e.g. `LoadGameEvent`, `FSDJumpEvent`, `DockedEvent`). Each type has:
  - Event name(s)
  - Strongly-typed EventArgs (properties match journal JSON)
  - Fired via `JournalWatcher.GetEvent<T>().Fired += handler`
- **Auxiliary JSON files** (same folder as journals):
  - **Cargo.json** – Current cargo; read via `ReadCargoJson()`.
  - **NavRoute.json** – Current navigation route; read via `ReadNavRouteJson()`.
  - **Market.json** – Market info; read via `ReadMarketInfo()`.

## What EDLA Has Ported / Uses

### 1. Journal monitoring (existing, aligned conceptually)

- EDLA’s **LogMonitor** (watchdog) + **SessionManager** already:
  - Watch the same journal directory.
  - Process journal lines as JSON.
  - Replay/history: initial scan of logs + periodic rescan; commander selection triggers full log revalidation.
- No change required; behavior is analogous to “process previous journals then go live.”

### 2. Verbose event display (extended)

- **Monitor screen** shows a single, human‑readable line per event (newest first, scroll down for older).
- Event text is built from the **event** type and key fields, inspired by the breadth of event types in EliteJournalReader (e.g. LoadGame, FSDJump, Docked, Undocked, Touchdown, Liftoff, Bounty, FactionKillBond, Died, Scan, SellExplorationData, MarketBuy/Sell, Missions, RefuelAll, RepairAll, SupercruiseEntry/Exit, FileHeader, plus generic fallback).
- Additional event types can be added in `main._format_event_verbose()` using the same pattern; the C# Events list is a good checklist (see “Event catalog” below).

### 3. Auxiliary JSON reader (new)

- **journal_aux_reader.py** – Reads optional Elite Dangerous files from the **journal directory** (same as `DEFAULT_LOG_DIR`):
  - **Cargo.json** – Current cargo (e.g. for a future “Cargo” panel or stats).
  - **NavRoute.json** – Current plotted route (e.g. for a “Route” or navigation panel).
  - **Market.json** – Market information (e.g. for trade/price display).
- APIs: `read_cargo()`, `read_nav_route()`, `read_market()`; return parsed dict or `None` if file missing/invalid.
- These mirror the C# `ReadCargoJson()`, `ReadNavRouteJson()`, and `ReadMarketInfo()` pattern.

### 4. Event catalog (reference only)

- The C# repo defines **200+** event types. EDLA does not implement a type per event; it uses one formatter with branches per event type and a generic fallback.
- For extending the log view or session stats, the Events folder is a useful reference for:
  - Event names (exact `"event"` string in JSON).
  - Which fields exist (e.g. LoadGame: Commander, Ship, StarSystem, Credits, etc.).
- Official field list: [Journal Manual v18](http://hosting.zaonce.net/community/journal/v18/Journal_Manual_v18.pdf).

## ODEliteTracker (Reference)

- **Repo:** https://github.com/WarmedxMints/ODEliteTracker  
- **Language:** C# (WPF), .NET 9  
- **Purpose:** Tracker for in-game activities with dedicated UIs and persistence.  
- **Features** (from the [README](https://github.com/WarmedxMints/ODEliteTracker)):
  - **Pirate Massacre Missions** – Track kill counts and progress per mission/faction.
  - **Trade Missions** – Track trade/courier mission progress.
  - **Colonisation Depot Progress** – Track colonisation-related objectives.
  - **Background Simulation (BGS) Activities** – Track influence and BGS-related events.
  - **Powerplay Activities** – Track merits, objectives, and power-specific data.
  - **Mining Sessions** – Track mining yield, materials, and session stats.
  - **Fleet Carriers** – Track carrier state, market, and operations.

EDLA does not replicate ODEliteTracker’s full UI or data model. The following are useful as **inspiration** for future EDLA features (same journal + optional API data):

| ODEliteTracker feature   | EDLA today / possible addition |
|--------------------------|---------------------------------|
| Missions                 | Current session: active + completed/failed; could add massacre/trade progress (kill counts, commodity counts). |
| BGS                      | Not tracked; could add FactionState, influence-style events if needed. |
| Powerplay                | Not tracked; could add Powerplay events (merits, vouchers, etc.). |
| Mining                   | Session stats (e.g. MiningRefined, materials); could add dedicated mining session view. |
| Fleet Carriers           | Not tracked; could add Carrier* events and optional CAPI. |
| Colonisation             | Not tracked; could add Colonisation* journal events. |

## Possible Future Ports

- **More event types in verbose display** – Add branches in `_format_event_verbose()` for Interdicted, FuelScoop, StartJump, ApproachBody, CodexEntry, MaterialCollected, and others from the Events list.
- **Cargo / Route / Market UI** – Use `journal_aux_reader` to drive a “Cargo” tab, “Current route” panel, or “Market” summary.
- **Mission progress (ODEliteTracker-style)** – For massacre missions: track kill counts per target faction; for trade/courier: track commodity/delivery progress (from MissionAccepted/MissionCompleted and related events).
- **BGS / Powerplay / Mining / Carriers / Colonisation** – Use ODEliteTracker’s feature set as a checklist for journal events and UI ideas (FactionState, Powerplay*, MiningRefined, Carrier*, Colonisation*).
- **Journal filename parsing** – Use a regex like `Journal(Beta)?.(timestamp).(part).log` for ordering or “current session” detection if needed.
- **Offset-based tailing** – For very large journals, only tail from last known offset (like the C# watcher) instead of scanning whole file; current EDLA approach is already efficient for typical use.

## File Locations (EDLA)

- Journal directory (watched): `config.DEFAULT_LOG_DIR`  
  (`%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous`)
- Auxiliary files read by EDLA:  
  `{DEFAULT_LOG_DIR}/Cargo.json`, `NavRoute.json`, `Market.json`
- Event formatting: `main.MonitorScreen._format_event_verbose()`
- Auxiliary reader: `journal_aux_reader.py`

## References

- [EliteJournalReader (GitHub)](https://github.com/WarmedxMints/EliteJournalReader)  
- [ODEliteTracker (GitHub)](https://github.com/WarmedxMints/ODEliteTracker) – Missions, BGS, Powerplay, mining, fleet carriers, colonisation.  
- [Journal Manual v18 (PDF)](http://hosting.zaonce.net/community/journal/v18/Journal_Manual_v18.pdf)  
- [Journal Manual v18 (Word)](http://hosting.zaonce.net/community/journal/v18/Journal_Manual_v18.doc)
