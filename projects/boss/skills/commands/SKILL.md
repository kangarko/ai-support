---
name: boss-commands-permissions
description: 'Commands, permissions, PlaceholderAPI variables, and global settings'
---

# Commands, Permissions, and Variables

## Overview

Boss provides a `/boss` command group (aliases: `/b`) with 18+ subcommands for creating, spawning, managing, finding, and removing Bosses. Commands are registered via `BossCommandGroup` extending `SimpleCommandGroup`, with each subcommand extending `BossSubCommand`. Permissions are declared in `Permissions.java` using `@Permission` and `@PermissionGroup` annotations. PlaceholderAPI integration is handled by `BossPlaceholders` extending `SimpleExpansion`. Global settings in `settings.yml` control spawning, fighting, health, death, variables, skills, and debug modes.

## Architecture

### Key Classes

- `BossCommandGroup` (command/BossCommandGroup.java): Extends `SimpleCommandGroup`.
- `BossSubCommand` (command/BossSubCommand.java): Abstract base class extending `SimpleSubCommand`.
- `BossEggAbstractCommand` (command/BossEggAbstractCommand.java): Extends `BossSubCommand`.
- `Permissions` (model/Permissions.java): Declares all plugin permissions using `@PermissionGroup` and `@Permission` annotations.
- `BossPlaceholders` (model/BossPlaceholders.java): Singleton extending `SimpleExpansion`.
- `Settings` (settings/Settings.java): Extends `SimpleSettings`.
- `BossCheatDisable` (model/BossCheatDisable.java): Enum with 3 values: FLIGHT, GOD_MODE, INVISIBILITY.

### Command Registration Flow

1. `BossCommandGroup` is annotated `@AutoRegister`, so it is discovered and instantiated by the Foundation framework at plugin startup.
2. `registerSubcommands()` calls `registerSubcommand(BossSubCommand.class)` which scans for all non-abstract classes extending `BossSubCommand` in the same package and registers them.
3. `registerDefaultSubcommands()` adds built-in commands: `reload`, `debug`, `dumplocale`.
4. A `PermsSubCommand` is registered with `Permissions.class` to generate the `/boss perms` permission listing.

## Common Issues & Solutions

- **Commands not working**: Ensure the player has the correct permission. Foundation auto-generates `boss.command.<subcommand>` permissions. Use `/boss perms` to see all permissions. Operators (OP) have all permissions by default.
- **Tab completion not showing Boss names**: Bosses must be loaded (valid YAML in `bosses/` folder). Run `/boss list` to verify loaded Bosses. Invalid YAML files are skipped with a console error.
- **PlaceholderAPI variables returning empty**: The nearest-Boss placeholders (`name`, `alias`, `health`, `location`, `top_damage*`) require the main thread. If called asynchronously (e.g., by CMI), they return empty and log a warning. Contact the calling plugin's developers to use main-thread variable replacement.
- **PlaceholderAPI variables not resolving at all**: Ensure PlaceholderAPI is installed and Boss is registered as an expansion. Check with `/papi list` that `boss` appears.
- **%boss_name% always empty**: The player must have recently damaged a Boss within `Variables.Nearby_Boss_Radius` blocks (default 20). Increase this value in settings.yml if needed.
- **Respawn placeholder shows "Spawned" always**: The Boss must have died at least once while tracked by the specified RESPAWN_AFTER_DEATH spawn rule. The rule must be assigned to the Boss. Verify the spawn rule name matches exactly (case-sensitive).
- **Health bar not appearing**: Check `Fighting.Health_Bar.Enabled` is true in settings.yml. The action bar only shows when a player damages a Boss, not when the Boss damages the player.
- **Disable_Cheats not working**: The cheat disable only triggers when a player attacks or is attacked by a Boss. It checks for FLIGHT (creative/allow flight), GOD_MODE (invulnerable), and INVISIBILITY (potion effect). Some plugins may re-enable these abilities.
- **Scan command not running**: `/boss scan` is console-only. It will not run from in-game. The command requires running twice for safety confirmation. Ensure no other region-manipulation tools (WorldEdit, VoxelSniper) are running simultaneously.
- **Relative coordinates (~) not working**: The `~` coordinate only works when the command sender is an in-game player, not from console. Console must specify absolute world/x/y/z values.
- **Debug mode not showing output**: Set `Debug: [spawning]` (or other sections) in settings.yml, then run `/boss reload`. Available sections: `spawning`, `skills`, `region-keep`, `unloaded`, `commands`, `health`. Multiple sections can be enabled simultaneously: `Debug: [spawning, skills, commands]`.
- **Command aliases conflict**: If another plugin uses `/boss`, change `Command_Aliases` in settings.yml. The first entry is the primary label. Do not remove it entirely; replace it with a different label.

## Key File Paths

- `src/main/java/org/mineacademy/boss/command/BossCommandGroup.java` - Main command group registration
- `src/main/java/org/mineacademy/boss/command/BossSubCommand.java` - Base subcommand class with Boss lookup and spawn helpers
- `src/main/java/org/mineacademy/boss/command/BossEggAbstractCommand.java` - Shared base for spawn/eggdrop commands with coordinate parsing
- `src/main/java/org/mineacademy/boss/command/MenuCommand.java` - /boss menu command
- `src/main/java/org/mineacademy/boss/command/NewCommand.java` - /boss new command
- `src/main/java/org/mineacademy/boss/command/SpawnCommand.java` - /boss spawn command
- `src/main/java/org/mineacademy/boss/command/SpawnPlayerCommand.java` - /boss spawnpl command
- `src/main/java/org/mineacademy/boss/command/EggCommand.java` - /boss egg command

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
