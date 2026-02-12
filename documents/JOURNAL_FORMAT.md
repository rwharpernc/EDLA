# Elite Dangerous Journal Format

**Author:** R.W. Harper  
**Last Updated:** 2026-02-12  
**License:** GPL-3.0

## Overview

Elite Dangerous creates journal files in JSON format, with one event per line. These files are located in:

```
%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\
```

In EDLA, this path can be overridden via the external config file; see [CONFIG.md](CONFIG.md).

## File Naming Convention

Journal files are named:
```
Journal.YYYYMMDDHHMMSS.01.log
```

Where:
- `YYYYMMDDHHMMSS` is the timestamp when the file was created
- `.01` indicates the file number (increments if multiple files exist)
- `.log` is the file extension

## File Structure

### FileHeader Event

Every journal file starts with a `FileHeader` event:

```json
{
  "timestamp": "2024-12-01T12:00:00Z",
  "event": "FileHeader",
  "part": 1,
  "language": "English",
  "gameversion": "4.0.0.1234",
  "build": "r123456"
}
```

### LoadGame Event

The `LoadGame` event contains commander information and is crucial for detection:

```json
{
  "timestamp": "2024-12-01T12:00:00Z",
  "event": "LoadGame",
  "Commander": "CommanderName",
  "FID": "F1234567890",
  "Horizons": true,
  "Odyssey": false,
  "Ship": "Sidewinder",
  "ShipID": 1,
  "ShipName": "My Ship",
  "ShipIdent": "ABC-123",
  "FuelLevel": 4.0,
  "FuelCapacity": 4.0,
  "GameMode": "Open",
  "Credits": 1000,
  "Loan": 0,
  "StarSystem": "Sol",
  "SystemAddress": 1234567890,
  "Body": "Earth",
  "BodyID": 1,
  "BodyType": "Planet"
}
```

**Key Fields:**
- `Commander`: The commander name (used for detection)
- `Ship`: Current ship type
- `StarSystem`: Current star system
- `Credits`: Current credit balance

## Common Event Types

### Station Events

**Docked:**
```json
{
  "timestamp": "2024-12-01T12:05:00Z",
  "event": "Docked",
  "StationName": "Abraham Lincoln",
  "StationType": "Coriolis",
  "StarSystem": "Sol",
  "SystemAddress": 1234567890,
  "MarketID": 1234567890,
  "StationFaction": {
    "Name": "Federal Navy"
  },
  "StationGovernment": "Democracy",
  "StationEconomy": "Industrial",
  "StationServices": ["dock", "refuel", "repair", "rearm"]
}
```

**Undocked:**
```json
{
  "timestamp": "2024-12-01T12:10:00Z",
  "event": "Undocked",
  "StationName": "Abraham Lincoln",
  "StationType": "Coriolis",
  "MarketID": 1234567890
}
```

### Travel Events

**FSDJump:**
```json
{
  "timestamp": "2024-12-01T12:15:00Z",
  "event": "FSDJump",
  "StarSystem": "Proxima Centauri",
  "SystemAddress": 9876543210,
  "StarClass": "M",
  "JumpDist": 4.24,
  "FuelUsed": 0.5,
  "FuelLevel": 3.5
}
```

**Location:**
```json
{
  "timestamp": "2024-12-01T12:20:00Z",
  "event": "Location",
  "StarSystem": "Proxima Centauri",
  "SystemAddress": 9876543210,
  "Body": "Proxima Centauri b",
  "BodyID": 1,
  "BodyType": "Planet",
  "Docked": false,
  "Latitude": 0.0,
  "Longitude": 0.0
}
```

### Combat Events

**Died:**
```json
{
  "timestamp": "2024-12-01T12:25:00Z",
  "event": "Died",
  "KillerName": "NPC Pirate",
  "KillerShip": "Eagle",
  "KillerRank": "Competent"
}
```

**Bounty:**
```json
{
  "timestamp": "2024-12-01T12:30:00Z",
  "event": "Bounty",
  "Rewards": [
    {
      "Faction": "Federal Navy",
      "Reward": 50000
    }
  ],
  "Target": "NPC Pirate",
  "TotalReward": 50000,
  "VictimFaction": "Pirates"
}
```

### Rank and Progress Events

The game sends `Rank` and `Progress` events (e.g. at session start and when ranks change). **Rank** includes numeric values for Combat, Trade, Explore, Empire, Federation, CQC, and (Odyssey) Mercenary, Exobiologist. **Progress** gives 0–100 percentage toward the next rank per category.

**Indexing for display:** Federation and Empire use 0 for “no rank” (Federation: 0=None, 1=Recruit … 14=Admiral; Empire: 0=None, 1=Outsider … 7=Baron … 14=King). Skill ranks (Combat, Trade, Explore, CQC, Mercenary, Exobiologist) are 0-based with 0 as the first rank (e.g. Combat 0=Harmless, 8=Elite). EDLA maps these to in-game rank names on the Home screen.

### Reputation Event

The game sends a `Reputation` event (e.g. when docking) with faction standings. EDLA supports two formats:

**Flat format** – faction names as keys, numeric value (0–100 or 0.0–1.0):
```json
{
  "timestamp": "2024-12-01T12:00:00Z",
  "event": "Reputation",
  "Federation": 75,
  "Empire": 50
}
```

**Factions array** – list of objects with `Name` and `Reputation` (number or text like "Friendly", "Allied"):
```json
{
  "timestamp": "2024-12-01T12:00:00Z",
  "event": "Reputation",
  "Factions": [
    { "Name": "Federation", "Reputation": 75 },
    { "Name": "Empire", "Reputation": "Friendly" }
  ]
}
```

Text reputation levels are mapped to 0–100 (e.g. Hostile=0, Unfriendly=25, Neutral=50, Cordial=60, Friendly=75, Allied=100).

## Event Processing

### Parsing Events

Each line in a journal file is a complete JSON object:

```python
import json

with open('journal.log', 'r') as f:
    for line in f:
        event = json.loads(line.strip())
        event_type = event.get('event')
        # Process event
```

### Important Considerations

1. **Encoding**: Files are UTF-8 encoded
2. **Newlines**: One event per line
3. **Timestamps**: ISO 8601 format (UTC)
4. **Missing Fields**: Not all events have all fields
5. **Event Order**: Events are chronological within a file
6. **Multiple Files**: New files created when game restarts

## Using Journal Data

### Commander Detection

The `LoadGame` event is used to detect commanders:

```python
if event.get('event') == 'LoadGame':
    commander = event.get('Commander')
    if commander:
        # Found commander
```

### Event Tracking

Track specific events by type:

```python
event_types = ['Docked', 'Undocked', 'FSDJump', 'Location']
if event.get('event') in event_types:
    # Track this event
```

### Statistics Collection

Extract statistics from events:

```python
if event.get('event') == 'LoadGame':
    ship = event.get('Ship')
    system = event.get('StarSystem')
    credits = event.get('Credits')
    # Store statistics
```

## Resources

- [Official Elite Dangerous Journal Documentation](https://elite-journal.readthedocs.io/)
- [EDDN (Elite Dangerous Data Network)](https://github.com/EDSM-NET/EDDN)
- [EDDB (Elite Dangerous Database)](https://eddb.io/)

## Notes

- Journal files are written in real-time as events occur
- Files may be locked while Elite Dangerous is running
- Old journal files are not deleted automatically
- File format may change with game updates

