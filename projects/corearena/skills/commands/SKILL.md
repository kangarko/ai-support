---
name: corearena-commands
description: 'All /arena subcommands, aliases, permissions, Allowed_Commands, and debug modes'
---

# CoreArena - Commands & Permissions

## Overview

CoreArena uses a single command group `/arena` with subcommands for all operations. The command group has multiple aliases. Each subcommand has its own permission node. The plugin also controls which commands players can run while inside an arena, and provides debug modes for troubleshooting.

## Architecture

### Key Classes

- `CoreArenaCommandGroup` (`command/CoreArenaCommandGroup.java`) -- The main command group. Auto-registered. Registers all subcommands from `AbstractCoreSubcommand` and adds a built-in `PermsSubCommand` that lists all permissions.
- `AbstractCoreSubcommand` (`command/AbstractCoreSubcommand.java`) -- Base class for all subcommands. Provides helper methods for arena/class/upgrade lookup, arena name tab completion, placeholder support, and common checks (playing, editing, console).
- `Permissions` (`util/Permissions.java`) -- Static final class containing all permission node constants, organized into `Commands`, `Chat`, `Bypass`, and `Tools` groups.

### Command Registration

All command classes in the `command/` package extend `AbstractCoreSubcommand`. They are auto-discovered and registered by `CoreArenaCommandGroup.registerSubcommand(AbstractCoreSubcommand.class)`. The `PermsSubCommand` is a built-in Foundation command that dumps all permissions.

## Command Aliases

Configured in `settings.yml`:

```yaml
Command_Aliases: [arena, ma, mobarena, corearena, ca]
```

The first alias (`arena`) is the primary label. All of these work interchangeably:
- `/arena <subcommand>`
- `/ma <subcommand>`
- `/mobarena <subcommand>`
- `/corearena <subcommand>`
- `/ca <subcommand>`

## Subcommands

### Player Commands

| Command | Aliases | Arguments | Description | Permission |
|---------|---------|-----------|-------------|------------|
| `/arena join` | `j` | `[arena]` | Join an arena. If no arena specified, detects from location or uses the only available arena. | `corearena.command.join.{arena}` |
| `/arena leave` | `l` | (none) | Leave the arena you are currently playing in. | `corearena.command.leave` |
| `/arena list` | `ls` | (none) | List all available arenas. | `corearena.command.list` |
| `/arena class` | `cl` | (none) | Open class selection menu (must be in arena lobby). | `corearena.command.class` |
| `/arena rewards` | `r` | (none) | Open the rewards purchase menu (cannot be used while in arena). | `corearena.command.rewards` |

### Admin Commands

| Command | Aliases | Arguments | Description | Permission |
|---------|---------|-----------|-------------|------------|
| `/arena new` | (none) | `<name>` | Create a new arena and enter edit mode. Name must be 3-50 chars, no spaces, no color codes. | `corearena.command.new` |
| `/arena edit` | `e` | `[arena]` | Toggle edit mode for an arena. If no arena specified, detects from location or current edit. Arena must be stopped. | `corearena.command.edit` |
| `/arena menu` | `m` | `[object]` | Open the main plugin menu, or a specific arena/class/upgrade menu. | `corearena.command.menu` |
| `/arena tools` | `t` | (none) | Open the setup tools menu (gives region/lobby/spawnpoint tools). | `corearena.command.tools` |
| `/arena items` | `i` | (none) | Open the special items menu (explosive bow, gold, etc.). | `corearena.command.items` |
| `/arena start` | (none) | `[arena]` | Force-start an arena. If STOPPED, starts lobby. If LOBBY, force-starts the game (bypasses minimum player check). | `corearena.command.start` |
| `/arena stop` | (none) | `[arena]` | Stop a running or lobby arena. | `corearena.command.stop` |
| `/arena find` | `f` | `[player]` or `[x y z]` or `[world x y z]` | Find which arena is at a location or which arena a player is in. | `corearena.command.find` |
| `/arena tp` | (none) | `[arena]` | Teleport to an arena's lobby point. | `corearena.command.tp` |
| `/arena nugget` | `n` | `[player]` or `<player> <set/give/take> <amount>` | View or manage a player's nugget balance. Without arguments, shows own balance. | `corearena.command.nugget` |
| `/arena level` | (none) | `[player]` or `<player> <give/set/take> <level>` | View or manipulate in-arena levels for a playing player. Target must be in a running arena. | `corearena.command.nugget` |
| `/arena toggle` | `tg` | `[arena]` | Enable or disable an arena. Arena must be stopped. | `corearena.command.edit` |
| `/arena egg` | (none) | `<monster>` | Get a monster spawn egg for use in arena mob spawners. | `corearena.command.edit` |
| `/arena remove` | `rm`, `delete` | `[arena]` | Permanently delete an arena and its config file. | `corearena.command.edit` |
| `/arena setclass` | (none) | `<player> [class]` | View or set a player's class during arena lobby. | `corearena.command.edit` |
| `/arena perms` | (none) | (none) | List all plugin permissions. | `corearena.command.edit` |
| `/arena reload` | (none) | (none) | Reload the plugin configuration. | `corearena.command.reload` |

### Built-in Foundation Commands

These are registered by Foundation framework automatically:
- `/arena reload` -- Reload configuration.
- `/arena perms` -- List all permissions with descriptions.

## Permissions

### Command Permissions

| Permission | Description |
|------------|-------------|
| `corearena.command.join.{arena}` | Join a specific arena. Replace `{arena}` with the lowercase arena name. |
| `corearena.command.leave` | Leave an arena. |
| `corearena.command.list` | List available arenas. |
| `corearena.command.rewards` | Open rewards menu. |
| `corearena.command.class` | Open class menu. |
| `corearena.command.edit` | Toggle edit mode, create/remove arenas, toggle arenas, get eggs, set classes. |
| `corearena.command.items` | Open special items menu. |
| `corearena.command.tools` | Open setup tools menu. |
| `corearena.command.menu` | Open admin menu. |
| `corearena.command.nugget` | Manage player nuggets. |
| `corearena.command.reload` | Reload the plugin. |
| `corearena.command.start` | Start pending arenas. |
| `corearena.command.stop` | Stop running arenas. |
| `corearena.command.new` | Create a new arena. |
| `corearena.command.find` | Find arenas at locations. |
| `corearena.command.tp` | Teleport to an arena. |
| `corearena.command.conversation` | Reply to server conversations. |

### Chat Permissions

| Permission | Description |
|------------|-------------|
| `corearena.chat.global` | Prefix chat with `!` to send to all server players instead of just arena players. |
| `corearena.chat.color.red` | Show admin name in red in arena chat. |

### Bypass Permissions

| Permission | Description |
|------------|-------------|
| `corearena.bypass.arenacommands` | Run any command while playing in an arena, bypassing `Allowed_Commands` list. |

### Tool Permissions

| Permission | Description |
|------------|-------------|
| `corearena.tools` | Use setup tools (region, lobby, spawnpoint selectors). |

### Class Permissions

| Permission | Description |
|------------|-------------|
| `corearena.class.{name}` | Access a specific class. `{name}` is the lowercase class filename. Configured per-class in `classes/<name>.yml`. |

## Allowed Commands (`settings.yml` -> `Arena.Allowed_Commands`)

While playing in an arena, players can only run commands listed here (unless they have `corearena.bypass.arenacommands`):

```yaml
Allowed_Commands:
  - /arena
  - /ma
  - /tell
  - /msg
  - /r
  - /ping
  - /tps
  - /lag
  - /warn
  - /kick
  - /tempban
  - /tempmute
  - /chc ach
  - /chc g
```

Commands not in this list are blocked for players inside arenas. The check compares the start of the typed command against each entry.

## Arena Chat (`settings.yml` -> `Arena.Chat`)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `Arena.Chat.Enabled` | boolean | true | Enable per-arena chat isolation. |
| `Arena.Chat.Ranged` | boolean | true | Only show chat to players in the same arena. |
| `Arena.Chat.Format` | string | `&3{player} &8> {operatorColor}{message}` | Chat format. Variables: `{arena}`, `{player}`, `{operatorColor}`, `{message}`, PlaceholderAPI. |
| `Arena.Chat.Global_Format` | string | `&8[&3{arena}&8] {operatorColor}{player}: &f{message}` | Format for `!`-prefixed global messages. |

Players with `corearena.chat.global` can prefix messages with `!` to broadcast to the entire server.

## Debug Modes (`settings.yml` -> `Debug`)

```yaml
Debug: []
```

Available debug sections (add to the list to enable):

| Section | What It Logs |
|---------|-------------|
| `arena` | Arena start/stop events, player join/leave with causes. |
| `mysql` | MySQL sync timing ("Updating MySQL data for x took y ms"). |
| `spawning` | Monster spawning details. |
| `next-phase` | Phase advancement logic, alive monster counting. Useful for diagnosing why phases are not advancing in `monsters` mode. |
| `alive-monsters` | Logs each entity counted as an alive monster. |

Example: `Debug: [arena, next-phase]`

## Global Arena Settings (Relevant to Commands)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `Arena.Store_Inventories` | boolean | true | Save/restore player inventory on join/leave. If false, players must have empty inventory. |
| `Arena.Restore_Saved_Max_Health` | boolean | true | Restore saved MAX_HEALTH attribute on leave. |
| `Arena.Give_Random_Class_If_Not_Selected` | boolean | true | Auto-assign random class on arena start if player has none. |
| `Arena.Keep_Own_Equipment_On_Death` | boolean | true | Keep own equipment on death if `Allow_Own_Equipment` is true. |
| `Arena.Move_Forgotten_Players` | boolean | true | Teleport players found in arenas on server join to spawn. |
| `Arena.Auto_Repair_Items` | boolean | false | Unlimited item durability in arenas. Requires restart. |
| `Arena.Display_Phase_Bar` | boolean | true | Show phase info in boss bar. |
| `Arena.Display_Mob_Health_Bar` | boolean | true | Show mob health in action bar. |
| `Arena.Hide_Death_Messages` | boolean | true | Suppress vanilla death messages in arenas. |
| `Arena.Console_Commands_For_Each` | boolean | false | Run `Console` commands per-player (enables `{player}` placeholder in Console section). |

## Other Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `Prefix` | string | `&5Arena //&7` | Chat message prefix. Set to `""` to disable. |
| `Locale` | string | `en_US` | Language file. Use `/arena dumplocale` to export for editing. |
| `Backup.Frequency` | time | 6 hours | Auto-backup frequency for `data.yml`. |
| `Sentry` | boolean | true | Send anonymized error reports. |

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
| `src/main/java/org/mineacademy/corearena/command/ToolsCommand.java` | `/arena tools` |
| `src/main/java/org/mineacademy/corearena/command/ItemsCommand.java` | `/arena items` |
| `src/main/java/org/mineacademy/corearena/command/ClassCommand.java` | `/arena class` |
| `src/main/java/org/mineacademy/corearena/command/RewardsCommand.java` | `/arena rewards` |
| `src/main/java/org/mineacademy/corearena/command/StartCommand.java` | `/arena start` |
| `src/main/java/org/mineacademy/corearena/command/StopCommand.java` | `/arena stop` |
| `src/main/java/org/mineacademy/corearena/command/FindCommand.java` | `/arena find` |
| `src/main/java/org/mineacademy/corearena/command/TpCommand.java` | `/arena tp` |
| `src/main/java/org/mineacademy/corearena/command/NuggetCommand.java` | `/arena nugget` |
| `src/main/java/org/mineacademy/corearena/command/LevelCommand.java` | `/arena level` |
| `src/main/java/org/mineacademy/corearena/command/ToggleCommand.java` | `/arena toggle` |
| `src/main/java/org/mineacademy/corearena/command/EggCommand.java` | `/arena egg` |
| `src/main/java/org/mineacademy/corearena/command/RemoveCommand.java` | `/arena remove` |
| `src/main/java/org/mineacademy/corearena/command/SetClassCommand.java` | `/arena setclass` |
| `src/main/java/org/mineacademy/corearena/util/Permissions.java` | All permission constants |
| `src/main/java/org/mineacademy/corearena/settings/Settings.java` | Global settings loader |
| `src/main/resources/settings.yml` | Global settings file |
