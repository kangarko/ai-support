---
name: commands
description: 'All commands, subcommands, permissions, and rule message variables'
---

# Commands & Permissions

## Overview

Protect uses a single command group (`/protect` or `/p`) with subcommands for scanning, inventory management, item inspection, database log browsing, import/export, playtime lookup, and administration. All permissions are defined in `Permissions.java` and organized into command, bypass, notify, and group categories.

## Architecture

### Key Classes

- `ProtectCommandGroup` (`command/ProtectCommandGroup.java`) - The main command group registered with Bukkit. Extends `SimpleCommandGroup`, registers all subcommands and a `PermsSubCommand` that lists all permissions from `Permissions.java`.
- `ProtectSubCommand` (`command/ProtectSubCommand.java`) - Abstract base for all subcommands, extends `SimpleSubCommand`.
- `Permissions` (`model/Permissions.java`) - Final class with nested static classes holding all permission string constants. Annotated with `@Permission` and `@PermissionGroup` for auto-documentation via `/protect perms`.

### Subcommand Classes

| Class | Sublabel | Description |
|-------|----------|-------------|
| `ScanCommand` | `scan\|s` | Manual inventory scan |
| `InvCommand` | `inv\|i` | View player inventory (online/offline) |
| `InvCloseCommand` | `invclose\|ic` | Close a player's open inventory |
| `ItemInfoCommand` | `iteminfo\|if` | Inspect held item properties |
| `EditItemCommand` | `edititem\|ei` | Edit held item properties |
| `LogsCommand` | `logs` | Browse database logs |
| `InspectCommand` | `inspect` | Print/remove container items |
| `ExportCommand` | `export` | Export item to NBT JSON |
| `ImportCommand` | `import` | Import item from NBT JSON |
| `PlaytimeCommand` | `playtime\|pt` | View player playtime |
| `PermsSubCommand` | `perms` | List all plugin permissions (built-in) |
| `ReloadSubCommand` | `reload` | Reload plugin configuration (built-in) |
| `RowCommand` | `row` | Internal command for log row manipulation (hidden from help) |

## Commands

### /protect scan

Manually scan a player's inventory against all rules.

```
/protect scan [player]
```

- If no player specified, scans yourself
- Uses `ScanCause.MANUAL` trigger
- Permission: default (inherited from command group)

### /protect inv

View the inventory of any player, including offline players.

```
/protect inv regular <name/uuid> [viewer]
/protect inv armor <name/uuid> [viewer]
/protect inv enderchest <name/uuid> [viewer]
```

- `regular` - Main inventory (hotbar, backpack)
- `armor` - Armor slots
- `enderchest` - Ender chest contents
- Optional `[viewer]` parameter opens the inventory for another player
- Supports offline players. Recently disconnected players autocomplete via `TemporaryStorage`
- Cannot view your own inventory for regular/armor types
- Permission: `protect.command.inv.{type}` where `{type}` is `regular`, `armor`, or `enderchest`
- Write permission: `protect.command.inv.write` (without this, inventory is read-only)

### /protect invclose

Force-close a player's currently open inventory.

```
/protect invclose <player>
```

- Permission: `protect.command.invclose`

### /protect iteminfo

Display detailed information about the held item.

```
/protect iteminfo meta [player]
/protect iteminfo string [player]
/protect iteminfo nbt [player]
```

- `meta` - Display name, type, durability, lore, enchants, potions, firework effects, model data, component string
- `string` - Bukkit's `ItemStack.toString()` output
- `nbt` - Full NBT tag from NBTItem (clickable to copy)
- If no player specified, inspects your own held item
- Player-only for self-inspection, but can specify another player

### /protect edititem

Edit properties of the item in your hand.

```
/protect edititem name <value>
/protect edititem name reset
/protect edititem lore <line1|line2>
/protect edititem lore reset
/protect edititem potion <type> <duration> <amplifier>
/protect edititem potion <type> reset
/protect edititem enchant <type> <level>
/protect edititem enchant reset
/protect edititem amount <number>
```

- Player-only command
- Name/lore support `&` color codes and MiniMessage
- Lore lines separated by `|`
- Potion duration in human format (e.g., `1m30s`, `2m`, `10s`). Types: https://mineacademy.org/potions
- Enchantment types: https://mineacademy.org/enchants. Adding unapplicable enchantments uses `addUnsafeEnchantment`
- Amount range: 1-999. Warning shown if >= 384 that Protect will confiscate on next scan

### /protect logs

Browse, filter, and manage database logs. See the logging-spy skill for full details.

```
/protect logs <items|command|transaction> [filters]
/protect logs <table> clear [filters]
/protect logs <table> ?
```

### /protect inspect

Print or remove items from a container you are looking at. See the logging-spy skill for full details.

```
/protect inspect print
/protect inspect remove <slot>
```

### /protect export

Export held item to JSON NBT. See the logging-spy skill for full details.

```
/protect export [player] [-console|-file|-chat]
```

### /protect import

Import item from JSON NBT. See the logging-spy skill for full details.

```
/protect import <player> chat <json>
/protect import <player> file <filename>
```

### /protect playtime

View player playtime statistics pulled from the server's `playerdata/` folder.

```
/protect playtime [player]
/protect playtime top
```

- `[player]` - Show playtime for a specific player (supports offline players)
- `top` - Show all players sorted by playtime (calculates async, may take a while on large servers)
- If no argument and run as player, shows your own playtime
- Console requires a player name argument

### /protect perms

List all plugin permissions with descriptions. Auto-generated from `@Permission` annotations in `Permissions.java`.

### /protect reload

Reload the plugin configuration, rules, and groups.

- Permission: `protect.command.reload`

### /protect row (hidden)

Internal command for manipulating database rows. Used by clickable chat components in `/protect logs`.

```
/protect row menu <table> <rowId>
/protect row remove <table> <rowId>
```

- `menu` - Opens a GUI menu showing items from the row (only for rows implementing `HoldsItems`)
- `remove` - Deletes the row from the database
- Player-only command
- Hidden from `/protect help`

## Permissions

### Command Permissions

| Permission | Description |
|------------|-------------|
| `protect.command.reload` | Reload the plugin |
| `protect.command.inv.regular` | View player's regular inventory |
| `protect.command.inv.armor` | View player's armor content |
| `protect.command.inv.enderchest` | View player's ender chest |
| `protect.command.inv.write` | Write to (modify) a player's inventory when viewing |
| `protect.command.invclose` | Close a player's open inventory |

### Bypass Permissions

| Permission | Description |
|------------|-------------|
| `protect.bypass.scan` | Inventory will never be scanned. False by default even for OPs |
| `protect.bypass.command` | Commands are ignored from command spy logging |
| `protect.bypass.transaction` | Shop transactions leave no traces |
| `protect.bypass.worldedit` | Bypass all WorldEdit block limits |

### Notify Permissions

| Permission | Description |
|------------|-------------|
| `protect.notify.commandspy` | Receive command spy broadcast alerts |
| `protect.notify.transaction` | Receive transaction broadcast alerts |
| `protect.notify.item` | Receive rule match broadcast alerts (global, from Rules.Broadcast) |

### Group Permission

| Permission | Description |
|------------|-------------|
| `protect.group.{group_name}` | Place player in a WorldEdit Total_Limit group. Replace `{group_name}` with the group key from settings.yml (e.g., `protect.group.vip`, `protect.group.moderators`) |

### Custom Rule Permissions

Rules can define their own permissions via operators:

- `require perm <custom.permission>` - Rule only applies if player has this permission
- `ignore perm <custom.permission>` - Rule is skipped if player has this permission
- `then notify <custom.permission> <message>` - Sends message to players with this permission

Example from default rules: `then notify protect.notify.unnaturalstack ...` and `then notify protect.notify.nbttoolong ...` are custom notify permissions defined directly in rules.

## Rule Message Variables

These variables can be used in rule operators (`then warn`, `then notify`, `then console`, `then command`, `then discord`, `then log`, `then toast`, `then title`, `then actionbar`, `then bossbar`, `then kick`, `then write`) and in broadcast/discord format strings.

### Player Variables

All standard Foundation/PlaceholderAPI variables are available via the `Variables.builder()` system. Additionally:

| Variable | Description |
|----------|-------------|
| `{player}` | Player name |
| `{player_name}` | Player name (alias) |
| `{player_uid}` | Player UUID |
| `{data_<key>}` | Value of a stored rule data key (set via `save key`) |

### Item Variables (Rule-specific)

| Variable | Description |
|----------|-------------|
| `{item_type}` | Material name in UPPER_CASE (e.g., `DIAMOND_SWORD`) |
| `{item_type_formatted}` | Material name capitalized (e.g., `Diamond Sword`) |
| `{item_amount}` | Item stack amount |
| `{rule_name}` | Name of the matched rule |
| `{rule_group}` | Name of the group (if rule has a group) |
| `{rule_match}` | The match pattern of the rule |
| `{rule_fine}` | The fine amount from `then fine` |

### Location Variables

| Variable | Description |
|----------|-------------|
| `{location}` | Full serialized location string (world, x, y, z) |
| `{world}` | World name |
| `{x}` | Block X coordinate |
| `{y}` | Block Y coordinate |
| `{z}` | Block Z coordinate |

### Scan Variables

| Variable | Description |
|----------|-------------|
| `{cause}` | The scan cause that triggered the rule (e.g., `player join`, `inventory open`, `manual`) |
| `{removed_amount}` | Number of excess items removed (when using `then confiscate excess`) |

### Broadcast/Log Format Variables

These are available in `settings.yml` format strings (Rules, Command_Log, Transaction_Log):

| Variable | Context | Description |
|----------|---------|-------------|
| `{date}` | All | Formatted date |
| `{server}` / `{server_name}` | All | Server name from Server_Name setting |
| `{location}` | All | Location string |
| `{world}` | All | World name |
| `{player}` | All | Player name |
| `{player_uid}` | All | Player UUID |
| `{gamemode}` | All | Player gamemode |
| `{rule_name}` | Items | Rule name |
| `{rule_match}` | Items | Rule match pattern |
| `{item_amount}` | Items | Confiscated item amount |
| `{item_type}` | Items | Confiscated item type |
| `{type}` | Command_Log | "spy" or "block" |
| `{command}` / `{message}` | Command_Log | The command text |
| `{plugin}` / `{plugin_name}` | Transaction_Log | Shop plugin name |
| `{transaction_type}` | Transaction_Log | "Buy" or "Sell" |
| `{price}` | Transaction_Log | Raw price |
| `{price_formatted}` | Transaction_Log | Price with currency |
| `{shop_owner}` | Transaction_Log | Shop owner name |
| `{shop_owner_uid}` | Transaction_Log | Shop owner UUID |
| `{amount}` | Transaction_Log | Transaction amount |

### After_Scan Command Variables

| Variable | Description |
|----------|-------------|
| `{player}` | Player name |
| `{date}` | Current date/time |
| `{material}` | Material name |
| `{location}` | Location string |

### Delay Variables

| Variable | Description |
|----------|-------------|
| `{delay}` | Remaining seconds until delay expires |
| `{player_delay}` | Remaining seconds until player delay expires |

## Common Issues & Solutions

1. **Command not working** - Verify the player has the required permission. Check `Command_Aliases` in settings.yml for the correct command prefix. Default aliases are `protect` and `p`.
2. **protect.command.inv.{type} not working** - Replace `{type}` with the actual type: `regular`, `armor`, or `enderchest`. Example: `protect.command.inv.regular`.
3. **protect.bypass.scan not working for OPs** - This permission is explicitly false by default even for operators. You must grant it via a permissions plugin, not rely on OP status. Alternatively, set `Ignore.Ops: true` in settings.yml.
4. **Variables not replacing** - Ensure you use curly braces: `{variable_name}`. Variables are context-dependent (item variables only work in rule operators, transaction variables only in transaction formats). Check for typos in variable names.
5. **Custom notify permission** - When using `then notify protect.notify.custom <message>`, the permission string is the first word after `then notify`. Everything after is the message.
6. **Offline player inventory issues** - `/protect inv` supports offline players by reading their `playerdata/*.dat` files. The player must have joined at least once. UUID lookup is attempted for the given name.
7. **/protect edititem amount warning** - Setting amount >= 384 triggers a warning because the default `over-64` rule will confiscate items with 65+ stacks, and `unnatural-stack` catches anything over the natural max.
8. **protect.group.{group_name} for WorldEdit** - This is the permission pattern for WorldEdit Total_Limit groups, not rule groups. Rule groups use `ignore perm` operator for bypass. The `{group_name}` must match the key in `WorldEdit.Total_Limit` map.
9. **/protect row errors** - This is an internal command invoked by clickable chat elements. If it errors, the row may have been deleted or the database may be disconnected. Re-run `/protect logs` to refresh.
10. **Playtime shows 0** - Playtime is read from the server's statistics system. If `spigot.yml` has `stats.disable-saving: true`, playtime tracking is unavailable and `require/ignore playtime` operators will throw an error.

## Key File Paths

- `src/main/java/org/mineacademy/protect/command/ProtectCommandGroup.java` - Main command group registration
- `src/main/java/org/mineacademy/protect/command/ProtectSubCommand.java` - Base subcommand class
- `src/main/java/org/mineacademy/protect/command/ScanCommand.java` - /protect scan
- `src/main/java/org/mineacademy/protect/command/InvCommand.java` - /protect inv
- `src/main/java/org/mineacademy/protect/command/InvCloseCommand.java` - /protect invclose
- `src/main/java/org/mineacademy/protect/command/ItemInfoCommand.java` - /protect iteminfo
- `src/main/java/org/mineacademy/protect/command/EditItemCommand.java` - /protect edititem
- `src/main/java/org/mineacademy/protect/command/LogsCommand.java` - /protect logs
- `src/main/java/org/mineacademy/protect/command/InspectCommand.java` - /protect inspect
- `src/main/java/org/mineacademy/protect/command/ExportCommand.java` - /protect export
- `src/main/java/org/mineacademy/protect/command/ImportCommand.java` - /protect import
- `src/main/java/org/mineacademy/protect/command/PlaytimeCommand.java` - /protect playtime
- `src/main/java/org/mineacademy/protect/command/RowCommand.java` - /protect row (hidden)
- `src/main/java/org/mineacademy/protect/model/Permissions.java` - All permission constants
- `src/main/java/org/mineacademy/protect/operator/ProtectOperator.java` - replaceExtraVariables method defines item/location/cause variables
- `src/main/java/org/mineacademy/protect/operator/Rule.java` - RuleCheck.replaceExtraVariables defines rule_name, rule_group, rule_match, item_type, item_amount variables
- `src/main/resources/settings.yml` - Command_Aliases and all format strings with variables
