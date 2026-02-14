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
- `Transaction` (`model/db/Transaction.java`) - Database row representing a shop transaction. Stores player, location, plugin name, transaction type (BUY/SELL), price, shop owner, item, and amount. Has multiple static `logPlayer` and `logServer` methods.
- `CommandLogListener` (`listener/CommandLogListener.java`) - Bukkit `PlayerCommandPreprocessEvent` listener. Checks if command matches `Command_List` regex patterns. If `Block` is true, cancels the event and sends a fake no-permission message.
- `ProtectRow` (`model/db/ProtectRow.java`) - Abstract base for all database rows. Stores common fields: server, player, playerUid, gamemode, date, location. Provides `broadcast()` method for in-game and Discord notifications, and `saveIfSenderNotBypasses()` for conditional database saving.
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

## Configuration (settings.yml)

### Command_Log Section

| Key | Default | Description |
|-----|---------|-------------|
| `Command_Log.Enabled` | `true` | Enable command spy |
| `Command_Log.Block` | `false` | Block matched commands instead of just logging |
| `Command_Log.Block_Fallback_Message` | No permission message | Shown when blocked and real command has no permission message |
| `Command_Log.Broadcast` | `true` | Notify admins with `protect.notify.commandspy` |
| `Command_Log.Broadcast_Format` | `&8[&d{type}&8]&f {player}&7: {message}` | In-game broadcast format |
| `Command_Log.Discord_Channel` | `none` | DiscordSRV channel name or `none` |
| `Command_Log.Discord_Format` | `[{server_name}] [{type}] ...` | Discord message format |
| `Command_Log.Command_List` | `/give`, `/i`, `/ban`, `/tempban`, `/gm`, `/gamemode`, `/op` | Regex patterns (case insensitive). Initial `/` or `//` is auto-escaped |

#### Command_Log Variables

| Variable | Description |
|----------|-------------|
| `{type}` | "spy" or "block" depending on `Block` setting |
| `{command}` / `{message}` | The full command text |
| `{player}` | Player name |
| `{player_uid}` | Player UUID |
| `{date}` | Formatted date |
| `{server}` / `{server_name}` | Server name from `Server_Name` setting |
| `{location}` | Player location |
| `{world}` | World name |
| `{gamemode}` | Player gamemode |

### Transaction_Log Section

| Key | Default | Description |
|-----|---------|-------------|
| `Transaction_Log.Enabled` | `true` | Enable transaction logging (requires restart) |
| `Transaction_Log.Broadcast` | `true` | Notify admins with `protect.notify.transaction` |
| `Transaction_Log.Broadcast_Format_Buy` | `&8[&d{plugin_name}&8]...` | Format for buy transactions |
| `Transaction_Log.Broadcast_Format_Sell` | `&8[&d{plugin_name}&8]...` | Format for sell transactions |
| `Transaction_Log.Discord_Channel` | `none` | DiscordSRV channel name or `none` |
| `Transaction_Log.Discord_Format_Buy` | `[{server_name}] ...` | Discord format for buys |
| `Transaction_Log.Discord_Format_Sell` | `[{server_name}] ...` | Discord format for sells |

#### Transaction_Log Variables

| Variable | Description |
|----------|-------------|
| `{plugin}` / `{plugin_name}` | Shop plugin name (e.g., "ChestShop") |
| `{transaction_type}` | "Buy" or "Sell" |
| `{price}` | Raw price number |
| `{price_formatted}` | Price with currency symbol |
| `{shop_owner}` | Shop owner name |
| `{shop_owner_uid}` | Shop owner UUID |
| `{item_type}` | Item material name (capitalized) |
| `{amount}` | Transaction amount |
| `{player}` | Buyer/seller name |
| `{player_uid}` | Buyer/seller UUID |
| `{date}` | Formatted date |
| `{server}` / `{server_name}` | Server name |
| `{location}` | Transaction location |
| `{world}` | World name |
| `{gamemode}` | Player gamemode |

## Commands

### /protect logs

Browse and manage database logs.

```
/protect logs <table> - Display all logs in the table
/protect logs <table> [filters] - Display filtered logs
/protect logs <table> clear - Delete all logs
/protect logs <table> clear [filters] - Delete filtered logs
/protect logs <table> ? - List available filters
```

Tables: `items`, `command`, `transaction`.

Filters are typed as `filter:value` (e.g., `date:1m player:Notch`). Available filters depend on the table and are listed with the `?` param. Results are paginated in chat with clickable navigation.

Each log entry in chat shows:
- A clickable `[X]` to delete the row
- Date (hover for full details, click to copy timestamp)
- Player name (hover for gamemode/UUID, click to copy UUID)
- Row-specific details (command text, item info with click-to-restore, transaction details)

### /protect inspect

Print or remove items from a container block you are looking at, without opening it (prevents crash items from affecting you).

```
/protect inspect print - Dumps all items to chat and a file in dumps/
/protect inspect remove <slot> - Clears a specific slot in the container
```

Player-only command. You must be looking at a container block within 6 blocks.

### /protect export

Serialize the held item to a JSON NBT string.

```
/protect export [player] - Copy to clipboard (clickable in chat)
/protect export [player] -console - Print to server console
/protect export [player] -file - Save to exports/ folder
/protect export [player] -chat - Print formatted JSON in chat
```

Requires a modern Minecraft version for JSON item serialization.

### /protect import

Deserialize a JSON NBT string and give the resulting item to a player.

```
/protect import <player> chat <json_string> - Import from chat input
/protect import <player> file <filename> - Import from exports/ folder
```

## Database Configuration (database.yml)

| Key | Default | Description |
|-----|---------|-------------|
| `Type` | `local` | `local` for SQLite, `remote` for MySQL/MariaDB |
| `Host` | `localhost:3306` | Remote database host and port |
| `Database` | empty | Remote database name |
| `User` | empty | Remote database user |
| `Password` | empty | Remote database password |
| `Line` | JDBC connection string | Custom JDBC connection template |

The `Remove_Entries_Older_Than` setting in `settings.yml` (default: `120 days`) automatically purges old entries from all tables.

When using remote database, the `Server_Name` setting in `settings.yml` must be set to uniquely identify the server on the network.

The required collation is `utf8mb4_unicode_520_ci` for Unicode/emoji support. MySQL 8.0 is recommended.

Database tables:
- `Protect_Command` - Command spy logs (Id, Date, Server, Location, World, Player, PlayerUid, Gamemode, Command)
- `Protect_Items` - Confiscated items (Id, Date, Server, Location, World, Player, PlayerUid, Gamemode, Items, RuleMatch, RuleName, Inventory)
- `Protect_Transaction` - Shop transactions (Id, Date, Server, Location, World, Player, PlayerUid, Gamemode, Plugin, TransactionType, Price, ShopOwner, ShopOwnerUid, Item, Amount)

## Bypass and Notify Permissions

| Permission | Description |
|------------|-------------|
| `protect.bypass.command` | Player's commands are not logged by command spy |
| `protect.bypass.transaction` | Player's shop transactions are not logged |
| `protect.notify.commandspy` | Receive in-game command spy broadcasts |
| `protect.notify.transaction` | Receive in-game transaction broadcasts |
| `protect.notify.item` | Receive in-game rule match broadcasts |

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
- `src/main/java/org/mineacademy/protect/command/LogsCommand.java` - /protect logs
- `src/main/java/org/mineacademy/protect/command/InspectCommand.java` - /protect inspect
- `src/main/java/org/mineacademy/protect/command/ExportCommand.java` - /protect export
- `src/main/java/org/mineacademy/protect/command/ImportCommand.java` - /protect import
- `src/main/resources/settings.yml` - Command_Log and Transaction_Log sections
- `src/main/resources/database.yml` - Database connection settings
