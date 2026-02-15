---
name: database
description: 'ChatControl database system: SQLite, MySQL, MariaDB, database.yml, player cache persistence, mail storage, log storage, UUID/name mapping, data migration, table schema, encoding. Use when diagnosing database connection issues, data migration, or storage problems.'
---

# Database System

## Overview

ChatControl uses a SQL database (SQLite default, MySQL/MariaDB optional) to persist player data, mail, logs, server settings, and UUID↔name mappings. All database access goes through the singleton `Database` class extending Foundation's `SimpleDatabase`.

## Architecture

### Key Classes
- `Database` (model/db/Database.java) — singleton database manager
- `PlayerCache` (model/db/PlayerCache.java) — player data row (extends `Row`)
- `Log` (model/db/Log.java) — log entry row
- `Mail` (model/db/Mail.java) — mail message row
- `ServerSettings` (model/db/ServerSettings.java) — per-server/network settings
- `ChatControlTable` (model/db/ChatControlTable.java) — table name enum
- `Migrator` (model/Migrator.java) — data.db → SQL migration

### Database Tables (ChatControlTable)

| Table | Purpose |
|-------|---------|
| `PLAYERS` | Player settings (channels, colors, tags, ignore, mute, spy, etc.) |
| `LOG` | Chat/command/sign action logs |
| `MAIL` | Mail messages |
| `SETTINGS` | Server-wide and network-wide settings (mutes, etc.) |

### PlayerCache Schema

| Column | Type | Purpose |
|--------|------|---------|
| `UUID` | VARCHAR | Player UUID (primary when UUID_LOOKUP=true) |
| `Name` | VARCHAR | Player name (primary when UUID_LOOKUP=false) |
| `Nick` | VARCHAR | Nickname (indexed for `/realname` lookups) |
| `Data` | TEXT/JSON | JSON blob containing all player settings |
| `LastModified` | BIGINT | Timestamp for inactive purging |

**Data JSON contains:**
```json
{
  "Chat_Color": "RED",
  "Chat_Decoration": "BOLD",
  "Tags": {"NICK": "<red>CoolNick", "PREFIX": "[VIP]"},
  "Tags_Colorless": {"NICK": "CoolNick"},
  "Channels": {"global": "WRITE", "admin": "READ"},
  "Left_Channels": ["ranged"],
  "Ignored_Players": ["uuid1", "uuid2"],
  "Toggled_Off_Parts": ["PRIVATE_MESSAGE"],
  "Ignored_Messages": {"TIMED": ["tips"]},
  "Warn_Points": {"global": 3, "spam": 1},
  "Unmute_Time": 1734567890000,
  "Spying_Sectors": ["CHAT", "COMMAND"],
  "Spying_Channels": ["admin"],
  "Reply_Player_Name": "Steve",
  "Rule_Data": {"chatbot_name": "Bot1"},
  "Auto_Responder": {"Book": "...", "Expiration": 1234}
}
```

## Common Issues & Solutions

### "Database connection failed"
1. Check `database.yml` Type/Host/Database/User/Password
2. MySQL requires the database to exist (created manually)
3. Ensure MySQL user has full permissions on the database
4. MySQL 8.0+ recommended
5. Restart required after config changes

### "Unicode/emoji characters broken"
- MySQL must use `utf8mb4_unicode_520_ci` collation
- Check `characterEncoding=UTF-8` in connection string
- SQLite handles unicode natively

### "Slow database warnings"
- Connections > 100ms are logged
- Causes proxy server-switch delays
- Solution: co-locate MySQL server, reduce latency, check MySQL performance
- SQLite is faster for single-server setups

### "Player data lost on restart"
- Check `Settings.CLEAR_DATA_IF_INACTIVE` — may be purging data
- Verify database file exists (SQLite: `chatcontrol.db` in plugin folder)
- For MySQL: verify table contents directly
- Multiple PlayerCache entries logged as warnings (indicates bugs)

### "Migration from SQLite to MySQL"
- Change `Type` to `remote`, fill MySQL details
- `Migrator` handles automatic data migration on startup
- Monitor console for migration progress

### "Nick lookup not finding player"
- Nick column is indexed — `Database.getCache(name)` checks both Name and Nick
- `PlayerCache.poll()` searches memory → online → database

## Key File Paths

- Database: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/model/db/Database.java`
- PlayerCache: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/model/db/PlayerCache.java`
- Log: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/model/db/Log.java`
- Mail: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/model/db/Mail.java`
- Tables: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/model/db/ChatControlTable.java`
- Migrator: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/model/Migrator.java`
- Config: `chatcontrol-bukkit/src/main/resources/database.yml`

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
