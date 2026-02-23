---
name: database
description: 'Troubleshooting database connections, encoding, migration, and data persistence'
---

# Database Troubleshooting

## Diagnostic Flow — "Database error / data lost"

1. Check `database.yml` Type/Host/Database/User/Password
2. For MySQL: database must exist (created manually), user needs full permissions
3. Check console for connection errors or slow warnings

## Common Mistakes

- **MySQL must use `utf8mb4_unicode_520_ci` collation** — other collations break unicode/emoji characters. Check `characterEncoding=UTF-8` in connection string
- **Connections >100ms are logged as warnings** — causes proxy server-switch delays. Co-locate MySQL server or switch to SQLite for single-server setups
- **`CLEAR_DATA_IF_INACTIVE` silently purges data** — players who haven't been online for the configured period lose all data (tags, channels, ignore lists, etc.). Users report "player data disappeared" — check this setting
- **Nick column is indexed for `/realname` lookups** — database-level optimization. Not user-facing but relevant for slow `/realname` queries
- **Migrator auto-migrates SQLite→MySQL on startup** — changing Type from `local` to `remote` triggers automatic migration. Monitor console for progress
- **Multiple PlayerCache entries = bug indicator** — if console logs warn about duplicate PlayerCache entries, it indicates a synchronization bug
