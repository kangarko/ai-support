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

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
