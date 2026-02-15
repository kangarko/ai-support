---
name: corearena-commands
description: 'All /arena subcommands, aliases, permissions, Allowed_Commands, and debug modes'
---

# CoreArena - Commands & Permissions

## Overview

CoreArena uses a single command group `/arena` with subcommands for all operations. The command group has multiple aliases. Each subcommand has its own permission node. The plugin also controls which commands players can run while inside an arena, and provides debug modes for troubleshooting.

## Architecture

### Key Classes

- `CoreArenaCommandGroup` (`command/CoreArenaCommandGroup.java`) -- The main command group.
- `AbstractCoreSubcommand` (`command/AbstractCoreSubcommand.java`) -- Base class for all subcommands.
- `Permissions` (`util/Permissions.java`) -- Static final class containing all permission node constants, organized into `Commands`, `Chat`, `Bypass`, and `Tools` groups.

### Command Registration

All command classes in the `command/` package extend `AbstractCoreSubcommand`. They are auto-discovered and registered by `CoreArenaCommandGroup.registerSubcommand(AbstractCoreSubcommand.class)`. The `PermsSubCommand` is a built-in Foundation command that dumps all permissions.

## Common Issues & Solutions

**"You don't have permission to join this arena"**
The player lacks `corearena.command.join.{arena}` where `{arena}` is the lowercase arena name. Each arena has its own join permission.

**Commands blocked while in arena**
Add the command to `Allowed_Commands` in settings.yml, or give the player `corearena.bypass.arenacommands`.

**`/arena start` says "not enough players"**
When used on a STOPPED arena, it starts the lobby (no player check). When used on a LOBBY arena, it force-starts but still requires the minimum player count. If 0 players are in lobby, it cannot start.

**`/arena edit` says "arena is already running"**
Stop the arena first with `/arena stop`.

**Cannot find arena with `/arena find`**
The player's location must be inside an arena's cuboid region. Use `/arena find <x> <y> <z>` with specific coordinates, or `/arena find <player>` to check if a specific player is in an arena.

**Nugget command shows 0 for offline player**
If MySQL is not enabled, data is loaded from local `data.yml`. The player must have played on this server. With MySQL, data syncs across servers.

**Debug not showing output**
The `Debug` value must be a YAML list: `Debug: [arena, next-phase]`. Restart or reload after changing.

## Key File Paths

| File | Purpose |
|------|---------|
| `src/main/java/org/mineacademy/corearena/command/CoreArenaCommandGroup.java` | Command group registration |
| `src/main/java/org/mineacademy/corearena/command/AbstractCoreSubcommand.java` | Base subcommand with helpers |
| `src/main/java/org/mineacademy/corearena/command/JoinCommand.java` | `/arena join` |
| `src/main/java/org/mineacademy/corearena/command/LeaveCommand.java` | `/arena leave` |
| `src/main/java/org/mineacademy/corearena/command/ListCommand.java` | `/arena list` |
| `src/main/java/org/mineacademy/corearena/command/NewCommand.java` | `/arena new` |
| `src/main/java/org/mineacademy/corearena/command/EditCommand.java` | `/arena edit` |
| `src/main/java/org/mineacademy/corearena/command/MenuCommand.java` | `/arena menu` |

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
