---
name: logging-spy
description: 'Command spy, transaction logging, database storage, Discord integration, and log browsing'
---

# Logging & Spy

## Overview

Protect provides two independent logging systems: Command Spy (logs commands matching regex patterns and optionally blocks them) and Transaction Log (hooks into shop plugins to log buy/sell transactions). Both systems store data in a database (SQLite or MySQL), support in-game browsing via `/protect logs`, broadcast to admins, and forward to Discord via DiscordSRV.

## Architecture

### Key Classes

- `CommandSpy` (`model/db/CommandSpy.java`) - Database row representing a logged command. Stores player, location, gamemode, server, and the command string. Has `log(Player, String)` static method that broadcasts and saves.
- `Transaction` (`model/db/Transaction.java`) - Database row representing a shop transaction. Stores player, location, plugin name, transaction type (BUY/SELL), price, shop owner, item, and amount. Has multiple static `logPlayer` and `logServer`...
- `CommandLogListener` (`listener/CommandLogListener.java`) - Bukkit `PlayerCommandPreprocessEvent` listener. Checks if command matches `Command_List` regex patterns. If `Block` is true, cancels the event and sends a fake no-permission message.
- `ProtectRow` (`model/db/ProtectRow.java`) - Abstract base for all database rows. Stores common fields: server, player, playerUid, gamemode, date, location. Provides `broadcast()` method for in-game and Discord notifications, and...
- `ProtectTable` (`model/db/ProtectTable.java`) - Enum of database tables: `COMMAND` (command spy), `ITEMS` (confiscated items), `TRANSACTION` (shop transactions). Each table defines its SQL schema.
- `Item` (`model/db/Item.java`) - Database row representing confiscated items. Stores items array, rule match pattern, rule name, and full inventory snapshot.
- `Database` (`model/db/Database.java`) - Singleton extending `SimpleDatabase`. Connects to SQLite (local) or MySQL/MariaDB (remote). On connect, loads player names and server names into `TemporaryStorage` for autocomplete.
- `LogsCommand` (`command/LogsCommand.java`) - The `/protect logs` command. Supports table selection, filters, pagination, and clearing.
- `InspectCommand` (`command/InspectCommand.java`) - The `/protect inspect` command. Prints or removes items from a container block the player is looking at.
- `ExportCommand` (`command/ExportCommand.java`) - The `/protect export` command. Serializes held item to JSON NBT string (clipboard, console, file, or chat).
- `ImportCommand` (`command/ImportCommand.java`) - The `/protect import` command. Deserializes JSON NBT string back to an ItemStack.

### Shop Hooks

Transaction logging integrates with these shop plugins via dedicated hook classes in `hook/`:

| Plugin | Hook Class | Notes |
|--------|-----------|-------|
| BlueShop 3 | `BlueShop3Hook` | |
| ChestShop | `ChestShopHook` | |
| EconomyShopGUI | `EconomyShopGUIHook` | |
| ExcellentShop | `ExcellentShopHook` | |
| QuickShop | `QuickShopHook` | |
| ShopGUI+ | `ShopGUIHook` | |
| Shop | `ShopHook` | |
| SignShop | `SignShopHook` | |

Each hook listens for the shop plugin's transaction event, extracts buyer, seller, item, price, and amount, then calls `Transaction.logPlayer()` or `Transaction.logServer()`.

## Common Issues & Solutions

1. **Commands not being logged** - Verify `Command_Log.Enabled: true`. Check that the command matches a regex in `Command_List`. The player must have permission to run the command (commands the player cannot execute are skipped). Players with `protect.bypass.command` are ignored.
2. **Transactions not logging** - Verify `Transaction_Log.Enabled: true` and restart the server (requires restart). Ensure the shop plugin is installed and recognized. Check that the player does not have `protect.bypass.transaction`.
3. **Discord messages not sending** - DiscordSRV must be installed and loaded. The channel name must match exactly. Verify the channel setting is not `none`.
4. **Database connection failed** - For remote, check Host, Database, User, Password in `database.yml`. Ensure `Server_Name` is set in `settings.yml`. The plugin falls back to SQLite on connection failure.
5. **/protect logs shows empty** - Check the table name (items, command, transaction). Old entries may have been purged by `Remove_Entries_Older_Than`. Try without filters first.
6. **Blocked commands showing wrong message** - The plugin tries to use the real command's permission message. If unavailable, it uses `Block_Fallback_Message`.
7. **/protect export/import errors** - These commands require a modern Minecraft version with `Bukkit.getUnsafe().serializeItemAsJson()` support.
8. **Regex in Command_List** - The initial `/` or `//` is automatically escaped. Matching is case insensitive. Example: `/give` matches `/give`, `/Give`, etc.

## Key File Paths

- `src/main/java/org/mineacademy/protect/model/db/CommandSpy.java` - Command spy row
- `src/main/java/org/mineacademy/protect/model/db/Transaction.java` - Transaction row
- `src/main/java/org/mineacademy/protect/model/db/Item.java` - Confiscated item row
- `src/main/java/org/mineacademy/protect/model/db/ProtectRow.java` - Base row with broadcast logic
- `src/main/java/org/mineacademy/protect/model/db/ProtectTable.java` - Table schema definitions
- `src/main/java/org/mineacademy/protect/model/db/Database.java` - Database connection singleton
- `src/main/java/org/mineacademy/protect/listener/CommandLogListener.java` - Command spy listener
- `src/main/java/org/mineacademy/protect/hook/` - Shop plugin hooks (BlueShop3Hook, ChestShopHook, etc.)

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
