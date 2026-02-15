---
name: commands
description: 'Commands, permissions, locale, and general plugin settings'
---

# Commands & Permissions

## Overview

Winter uses a command group system where `/winter` (alias `/wt`) is the root command with multiple subcommands. The command group is auto-registered via `@AutoRegister` on `WinterCommandGroup`. Subcommands extend `WinterSubCommand` (which extends Foundation's `SimpleSubCommand`). The plugin also registers a built-in `PermsSubCommand` that lists all permissions from the `Permissions` class. Default subcommands (reload, dumplocale) are provided by Foundation's `SimpleCommandGroup.registerDefaultSubcommands()`.

## Architecture

### Key Classes

- `WinterCommandGroup` -- Annotated with `@AutoRegister`.
- `WinterSubCommand` -- Abstract base extending `SimpleSubCommand`.
- `SnowCommand` -- Sublabel: `snow|s`.
- `PopulateCommand` -- Sublabel: `populate|p`.
- `PsychoCommand` -- Sublabel: `psycho|ps`.
- `Permissions` -- Contains all permission node constants in two inner classes: `Commands` (annotated with `@PermissionGroup("Command permissions.")`) and `Chest` (annotated with `@PermissionGroup("Chest-related permissions.")`).
- `Settings` -- Extends Foundation's `SimpleSettings`.

### Command Registration Flow

1. `WinterCommandGroup` is auto-discovered and instantiated by Foundation via `@AutoRegister`.
2. `registerSubcommands()` is called: registers `WinterSubCommand.class` (Foundation scans for non-abstract subclasses: `SnowCommand`, `PopulateCommand`, `PsychoCommand`), then `registerDefaultSubcommands()` adds Foundation's built-in `reload` and `dumplocale` commands, then `PermsSubCommand` is added.
3. The command group registers under aliases defined in `Command_Aliases` (default: `[winter, wt]`). The first alias is the primary label.

## Common Issues & Solutions

| Issue | Cause | Solution |
|---|---|---|
| `/winter` not recognized | Plugin failed to load or incompatible platform | Check console for errors. Folia and Luminol are not supported |
| `/wt` not working | Alias conflict with another plugin | Change `Command_Aliases` in settings.yml |
| "You don't have permission" | Missing permission node | Grant the appropriate `winter.command.*` or `winter.chest.*` permission |
| `/winter populate` hangs server | Region scanning is intentionally synchronous | This is expected behavior. Wait for completion. Console warnings about "server not responding" can be ignored |
| `/winter populate` not from console | Command is console-only by design | Run from the server console, not in-game |
| `/winter reload` not applying terrain changes | Terrain.Snow_Generation does not support reload | Restart the server for terrain setting changes |
| `/winter snow` not working | Player lacks `winter.command.snow` permission | Grant the permission |
| Locale messages showing keys | Locale file corrupted or missing | Delete the locale file and restart to regenerate, or run `/winter dumplocale` |
| Prefix not showing | `Prefix` set to empty or `none` | Set a valid prefix in settings.yml |
| Sentry errors in console | `Sentry: true` sending reports | Set `Sentry: false` to disable anonymous error reporting |

## Key File Paths

- Settings: `src/main/resources/settings.yml` (Command_Aliases, Prefix, Locale, Sentry, Worlds)
- Settings model: `src/main/java/org/mineacademy/winter/settings/Settings.java`
- Locale: `src/main/resources/lang/en_US.json`
- Command group: `src/main/java/org/mineacademy/winter/command/WinterCommandGroup.java`
- Subcommand base: `src/main/java/org/mineacademy/winter/command/WinterSubCommand.java`
- Snow command: `src/main/java/org/mineacademy/winter/command/SnowCommand.java`
- Populate command: `src/main/java/org/mineacademy/winter/command/PopulateCommand.java`
- Psycho command: `src/main/java/org/mineacademy/winter/command/PsychoCommand.java`

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
