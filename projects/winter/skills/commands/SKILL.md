---
name: commands
description: 'Commands, permissions, locale, and general plugin settings'
---

# Commands & Permissions

## Overview

Winter uses a command group system where `/winter` (alias `/wt`) is the root command with multiple subcommands. The command group is auto-registered via `@AutoRegister` on `WinterCommandGroup`. Subcommands extend `WinterSubCommand` (which extends Foundation's `SimpleSubCommand`). The plugin also registers a built-in `PermsSubCommand` that lists all permissions from the `Permissions` class. Default subcommands (reload, dumplocale) are provided by Foundation's `SimpleCommandGroup.registerDefaultSubcommands()`.

## Architecture

### Key Classes

- `WinterCommandGroup` -- Annotated with `@AutoRegister`. Extends `SimpleCommandGroup`. Registers `WinterSubCommand` implementations (discovered via the class reference), default subcommands (reload, dumplocale), and a `PermsSubCommand` for the permissions listing.
- `WinterSubCommand` -- Abstract base extending `SimpleSubCommand`. Constructor takes the sublabel string (e.g. `"snow|s"`).
- `SnowCommand` -- Sublabel: `snow|s`. Player-only. Toggles snow particles per-player via `PlayerData.setSnowEnabled()`. Shows `command-snow-on` or `command-snow-off` locale messages. Permission: `winter.command.snow`.
- `PopulateCommand` -- Sublabel: `populate|p`. Console-only. Usage: `<add|remove> <world>`. Requires MC 1.7.10+. First invocation shows a detailed warning about region manipulation risks and estimated duration. Second invocation kicks all players, enables whitelist, and launches `WinterRegionCleaner` to scan all region files in the world and add/remove snow blocks. Respects `Do_Not_Place_On` and `Ignore_Biomes` settings. After completion, disables whitelist. Permission: `winter.command.populate`. Tab-completes `add`/`remove` and world names.
- `PsychoCommand` -- Sublabel: `psycho|ps`. Player-only. Spawns a Psycho snowman at the player's location via `PsychoMob.spawn()`. Fails with an error if the MC version is incompatible. Permission: `winter.command.psycho`.
- `Permissions` -- Contains all permission node constants in two inner classes: `Commands` (annotated with `@PermissionGroup("Command permissions.")`) and `Chest` (annotated with `@PermissionGroup("Chest-related permissions.")`). Each field is annotated with `@Permission("description")`.
- `Settings` -- Extends Foundation's `SimpleSettings`. Loads all configuration from `settings.yml`. Root-level settings: `ALLOWED_WORLDS` (loaded as `IsInList<String>`), `Command_Aliases`, `Prefix`, `Locale`, `Sentry`.

### Command Registration Flow

1. `WinterCommandGroup` is auto-discovered and instantiated by Foundation via `@AutoRegister`.
2. `registerSubcommands()` is called: registers `WinterSubCommand.class` (Foundation scans for non-abstract subclasses: `SnowCommand`, `PopulateCommand`, `PsychoCommand`), then `registerDefaultSubcommands()` adds Foundation's built-in `reload` and `dumplocale` commands, then `PermsSubCommand` is added.
3. The command group registers under aliases defined in `Command_Aliases` (default: `[winter, wt]`). The first alias is the primary label.

## Configuration

### General Settings (settings.yml)

```yaml
Command_Aliases: [winter, wt]     # Command aliases, first is primary label
Prefix: "&f&lWinter &8//&7"       # Chat message prefix
Locale: en_US                      # Language file (from lang/ folder)
Sentry: true                       # Send anonymized error reports to sentry.io
Worlds:
  - '*'                            # Enabled worlds, '*' for all
```

### Commands

| Command | Aliases | Usage | Permission | Player/Console | Description |
|---|---|---|---|---|---|
| `/winter snow` | `/winter s` | `/winter snow` | `winter.command.snow` | Player only | Toggle snow particles on/off for yourself |
| `/winter populate` | `/winter p` | `/winter populate <add\|remove> <world>` | `winter.command.populate` | Console only | Add or remove snow blocks from an entire world by scanning region files. First run shows warnings, second run executes. Kicks all players and enables whitelist during operation. |
| `/winter psycho` | `/winter ps` | `/winter psycho` | `winter.command.psycho` | Player only | Spawn a hostile Psycho snowman at your location |
| `/winter perms` | -- | `/winter perms` | -- | Any | List all plugin permissions with descriptions |
| `/winter reload` | `/winter rl` | `/winter reload` | `winter.command.reload` | Any | Reload plugin configuration (Terrain.Snow_Generation changes require full restart) |
| `/winter dumplocale` | -- | `/winter dumplocale` | -- | Any | Copy the active locale file to the plugin folder for editing |

### All Permissions

**Command Permissions (`@PermissionGroup("Command permissions.")`)**

| Permission | Description |
|---|---|
| `winter.command.region` | Access the /winter region command |
| `winter.command.populate` | Access the /winter populate command |
| `winter.command.snow` | Access the /winter snow command |
| `winter.command.reload` | Access the /winter reload command |
| `winter.command.psycho` | Access the /winter psycho command |

**Chest Permissions (`@PermissionGroup("Chest-related permissions.")`)**

| Permission | Description |
|---|---|
| `winter.chest.gift` | Place a gift chest ([Gift] sign) |
| `winter.chest.dated` | Place a dated chest ([Dated] sign) |
| `winter.chest.timed` | Place a timed chest ([Timed] sign) |
| `winter.chest.admin` | Bypass chest protection and open everyone's chests |

### Locale Messages (lang/en_US.json)

**Command-related keys:**

| Key | Default | Context |
|---|---|---|
| `command-snow-off` | `<red>You no longer see snowing particles.` | Player disabled snow particles |
| `command-snow-on` | `<white>You now see snowing particles.` | Player enabled snow particles |

**Chest-related keys:**

| Key | Default | Context |
|---|---|---|
| `boxed-chest-open` | Multi-line "Opening a gift chest..." | Shown when looting an infinite chest |
| `boxed-chest-preview` | Multi-line "Previewing a gift chest!" | Shown on dated chest preview |
| `chest-break-admin` | `<red>You just broke a (part of a) public gift chest.` | Admin breaking a chest |
| `chest-break-admin-sign` | `<red>You just broke a gift chest sign.` | Admin breaking a sign |
| `chest-break-own` | `<red>You just broke (a part of) your own gift chest.` | Owner breaking own chest |
| `chest-break-own-sign` | `<red>You just broke your own gift chest sign.` | Owner breaking own sign |
| `chest-create-success` | `<gold>Successfully placed a new Winter sign.` | Sign creation success |
| `chest-dated-limit` | `<red>You have already opened this chest!` | Dated chest max opens reached |
| `chest-dated-not-ready` | `<red>This chest is only accessible {accessibility}.` | Dated chest outside date range |
| `chest-expand-own` | `<dark_green>You just expanded a locked gift chest.` | Owner expanding chest |
| `chest-format-dated` | Date format hint | Invalid dated sign format |
| `chest-format-gift` | Gift format hint | Invalid gift sign format |
| `chest-format-timed` | Timed format hint | Invalid timed sign format |
| `chest-illegal-access` | `<red>Hey, this gift chest is not for you :)` | Unauthorized private chest access |
| `chest-illegal-break` | `<red>Hey, you cannot destroy this gift chest :)` | Unauthorized chest break |
| `chest-illegal-break-sign` | `<red>Hey, you cannot destroy this gift chest sign :)` | Unauthorized sign break |
| `chest-illegal-expand` | `<red>Hey, you cannot expand this gift chest :)` | Unauthorized chest expansion |
| `chest-illegal-inventory-click` | `<red>You cannot manipulate items in this preview!` | Click in preview inventory |
| `chest-illegal-place` | `<red>Hey, you cannot place things on a Winter chest!` | Sneaking + right-click on chest |
| `chest-invalid-format` | `<red>Sign has invalid format! Specify {format}.` | Wrong sign format |
| `chest-no-player` | `<red>Please specify which players should receive this gift...` | Gift sign without receivers |
| `chest-no-sign` | `<red>Place the {sign} sign on a chest!` | Sign not on a chest |
| `chest-open-admin` | `<dark_green>You are now viewing a locked gift chest's content.` | Admin opening locked chest |
| `chest-open-admin-dated` | `<gold>Warning: You've bypassed this chest date limit.` | Admin bypassing date |
| `chest-open-own` | `<gold>Browsing your own Winter chest content ...` | Owner viewing own chest |
| `chest-open-private` | `<gold>This gift chest is for you, enjoy it! :)` | Named receiver opening gift |
| `chest-open-public` | `<gold>Here you go, enjoy this free gift chest! :)` | Public gift chest opened |
| `chest-timed-limit` | `<red>This chest can only be looted {limit} time(s)!` | Timed chest max uses reached |
| `chest-timed-not-ready` | `<red>Chest will be ready in {time}.` | Timed chest cooldown active |
| `part-at`, `part-between`, `part-on` | Localized prepositions | Used in dated chest messages |

To customize messages, run `/winter dumplocale` to export the locale file to the plugin folder, then edit it.

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
- Permissions: `src/main/java/org/mineacademy/winter/model/Permissions.java`
- Plugin bootstrap: `src/main/java/org/mineacademy/winter/WinterPlugin.java`
- Player data (snow toggle): `src/main/java/org/mineacademy/winter/model/PlayerData.java`
