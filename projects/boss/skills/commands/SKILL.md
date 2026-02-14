---
name: boss-commands-permissions
description: 'Commands, permissions, PlaceholderAPI variables, and global settings'
---

# Commands, Permissions, and Variables

## Overview

Boss provides a `/boss` command group (aliases: `/b`) with 18+ subcommands for creating, spawning, managing, finding, and removing Bosses. Commands are registered via `BossCommandGroup` extending `SimpleCommandGroup`, with each subcommand extending `BossSubCommand`. Permissions are declared in `Permissions.java` using `@Permission` and `@PermissionGroup` annotations. PlaceholderAPI integration is handled by `BossPlaceholders` extending `SimpleExpansion`. Global settings in `settings.yml` control spawning, fighting, health, death, variables, skills, and debug modes.

## Architecture

### Key Classes

- `BossCommandGroup` (command/BossCommandGroup.java): Extends `SimpleCommandGroup`. Annotated with `@AutoRegister` for automatic registration. In `registerSubcommands()`, it registers all `BossSubCommand` subclasses, default subcommands (reload, debug, dumplocale), and a `PermsSubCommand` for `/boss perms` using `Permissions.class`.
- `BossSubCommand` (command/BossSubCommand.java): Abstract base class extending `SimpleSubCommand`. Provides `findBoss(name)` helper that validates Boss existence against all loaded Bosses. Provides `spawnBosses(spawnEggs, location, indexForBossNames)` that parses pipe-delimited Boss names (e.g., `Blaze|Zombie`) and supports `random` keyword to spawn a random Boss. Handles chunk loading/unloading if the target chunk is not loaded.
- `BossEggAbstractCommand` (command/BossEggAbstractCommand.java): Extends `BossSubCommand`. Shared base for `SpawnCommand` and `EggDropCommand`. Provides `parseCoordinate(index)` that supports `~` for relative player coordinates and numeric values. Shares tab completion logic for world, coordinates, and Boss names.
- `Permissions` (model/Permissions.java): Declares all plugin permissions using `@PermissionGroup` and `@Permission` annotations. Groups: Command, Use, Spawn, Bypass. Used by `PermsSubCommand` to generate `/boss perms` output.
- `BossPlaceholders` (model/BossPlaceholders.java): Singleton extending `SimpleExpansion`. Registered with PlaceholderAPI. The `onReplace(audience, params)` method parses underscore-delimited args to resolve Boss-specific, player-specific, and region-specific placeholders. Some placeholders require the main thread (name, alias, health, location, top_damage) and will warn if called asynchronously.
- `Settings` (settings/Settings.java): Extends `SimpleSettings`. Loads all values from `settings.yml`. Contains inner classes: Spawning (with Integration subclass), Fighting (with HealthBar and CitizensRetarget subclasses), Health, Death, Variables, Skills, PreventVanillaMobs. Also loads SORT_BY_TYPE at the root level.
- `BossCheatDisable` (model/BossCheatDisable.java): Enum with 3 values: FLIGHT, GOD_MODE, INVISIBILITY. Used by `Settings.Fighting.DISABLE_CHEATS` to disable player abilities during Boss fights.

### Command Registration Flow

1. `BossCommandGroup` is annotated `@AutoRegister`, so it is discovered and instantiated by the Foundation framework at plugin startup.
2. `registerSubcommands()` calls `registerSubcommand(BossSubCommand.class)` which scans for all non-abstract classes extending `BossSubCommand` in the same package and registers them.
3. `registerDefaultSubcommands()` adds built-in commands: `reload`, `debug`, `dumplocale`.
4. A `PermsSubCommand` is registered with `Permissions.class` to generate the `/boss perms` permission listing.

## Configuration

### All /boss Subcommands

#### /boss menu [boss] [player]
Aliases: `m`. Opens the main Boss GUI. If a Boss name is provided, opens that Boss's edit menu directly. Optionally specify a player to open the menu for them. Requires `boss.command.menu` permission.

#### /boss new <entityType>
Aliases: `create`, `add`. Creates a new Boss of the given entity type. Opens a chat prompt asking for the Boss name. Tab completes valid entity types from `Boss.getValidEntities()`. The player must not already be in a server conversation.

#### /boss spawn <world x y z> <boss1|boss2|random>
Spawns Boss(es) at the specified world coordinates. Supports `~` for relative player coordinates (X, Y, Z individually). Multiple Bosses can be separated with `|`. Use `random` to spawn a random Boss. Examples: `/boss spawn ~ ~ ~ ~ Blaze`, `/boss spawn minigames 100 15 50 Blaze|Zombie`.

#### /boss spawnpl <player> <boss1|boss2|random>
Aliases: `spawnpl`. Spawns Boss(es) near a target player. The Boss is placed 2 blocks behind the player's look direction, adjusted upward if the block is not air. Supports pipe-delimited names and `random`.

#### /boss egg <boss> [player] [amount]
Aliases: `e`. Gives a Boss spawn egg to the player (or yourself if no player specified). Optional amount parameter (defaults to 1). If the player's inventory is full, leftover eggs are dropped on the floor.

#### /boss eggdrop <world x y z> <boss1|boss2|random>
Drops Boss egg item(s) at the specified world coordinates. Same coordinate system as `/boss spawn` with `~` support. Supports pipe-delimited names and `random`.

#### /boss butcher <radius/world/*> [boss]
Aliases: `b`. Kills alive Bosses in loaded chunks. Three modes: numeric radius (around the player), world name (all Bosses in that world), or `*` (all Bosses in all worlds). Optionally filter by Boss name. Only affects loaded chunks; use `/boss scan` for unloaded chunks. Max radius: 10,000 blocks.

#### /boss list
Aliases: `l`. Lists all installed Boss names. Each name is clickable to open that Boss's menu via `/boss menu <name>`.

#### /boss remove <boss>
Aliases: `rm`. Permanently deletes a Boss configuration file and removes it from the loaded Boss list.

#### /boss find [boss/*] [world]
Aliases: `f`. Lists all alive Bosses in loaded chunks with their locations, health, and entity info. Each entry has clickable buttons to kill (`[X]`) or teleport to (`[>]`) the Boss via UUID. Defaults to all Bosses in all worlds if no arguments given. Uses paginated chat output.

#### /boss scan <world> [boss1|boss2]
Console-only command. Scans all chunks on disk (including unloaded) in the specified world and removes Boss entities. Requires running twice: first run displays a warning with estimated duration and safety instructions, second run executes the scan. Kicks all players for safety. May take minutes to hours depending on world size.

#### /boss location <params...>
Aliases: `loc`. Manages Boss spawn locations. Sub-parameters:
- `new` / `n` <name>: Creates a new location using the location tool (given to the player).
- `tool` / `t`: Gives the location creation tool to the player.
- `point` / `p`: Sets your feet position as a location.
- `list` / `l`: Lists all locations with clickable remove, visualize, and teleport buttons.
- `rem` / `rm` <name>: Removes a location permanently.
- `view` / `v` [name]: Visualizes a specific location (or all nearby within 100 blocks) for 10 seconds.
- `tp` <name>: Teleports to a location's center.

#### /boss uid <tp/tpto/kill/nbt> <uuid>
Manages a specific entity by its UUID. Operations:
- `tp <uuid>`: Teleport to the entity.
- `tpto <uuid> <world> <x> <y> <z>`: Teleport the entity to a location. Supports `~` for relative coordinates.
- `kill <uuid>`: Silently destroys the entity (removes passengers and NPC if applicable).
- `nbt <uuid>`: Dumps the entity's NBT data to console. If under 1000 characters, also shows in chat with click-to-copy.

#### /boss biome [player]
Shows what biome the player (or specified player) is standing in. Displays coordinates and biome name.

#### /boss skull <name/url/uuid/base64> <value> [player]
Gives a player skull item. Useful for placing on Boss heads. Four modes: `name` (player name), `url` (texture URL), `uuid` (player UUID), `base64` (Base64 texture string). Optionally specify a target player.

#### /boss perms
Lists all registered permissions with their descriptions. Generated automatically from the `@Permission` and `@PermissionGroup` annotations in `Permissions.java`.

#### /boss countunloaded <save/load> OR <world> <boss/all>
Hidden command (not shown in help). Debugs unloaded Boss tracking. `save` writes unloaded Bosses to file, `load` reads them back. With world and Boss name (or `all`), shows counts in loaded and unloaded chunks. Requires Paper server for unloaded tracking.

#### /boss reload
Built-in Foundation command. Reloads all configuration files (settings.yml, localization, Boss files, spawn rules).

#### /boss debug [section]
Built-in Foundation command. Toggles debug mode for specific sections.

#### /boss dumplocale
Built-in Foundation command. Exports the localization file to the plugin's data folder for editing.

### Permissions

#### Command Permissions
- `boss.command.menu`: Open Boss menu by clicking with a Boss egg or use `/boss menu` command.
- `boss.command.<subcommand>`: Auto-generated by Foundation for each subcommand (e.g., `boss.command.spawn`, `boss.command.new`, `boss.command.butcher`, `boss.command.egg`, etc.).

#### Use Permissions
- `boss.use.spawneregg`: Use the Boss spawner egg to spawn a Boss. Also requires `boss.spawn.<bossName>` for each specific Boss.
- `boss.use.inspect`: Use the Boss Egg to click a Boss to find more information.
- `boss.use.tamer`: Use the Boss Tamer Tool to edit owners of an entity.

#### Spawn Permissions
- `boss.spawn.{boss}`: Spawn a specific Boss through a spawner egg. Replace `{boss}` with the Boss name (case-sensitive).
- `boss.airspawn`: Right-click air while holding a Boss Egg to spawn Bosses at a distance.

#### Bypass Permissions
- `boss.bypass.claim`: Use Boss Egg in protected claims such as GriefPrevention, Residence, Towny, etc.

### PlaceholderAPI Variables

All placeholders use the `%boss_<params>%` format. The `args` array is split by underscores.

#### Nearest Boss Placeholders (Require Main Thread)
These find the closest Boss that the player has recently damaged, within `Variables.Nearby_Boss_Radius` blocks (default 20):
- `%boss_name%`: The Boss's internal name.
- `%boss_alias%`: The Boss's display alias (with color codes).
- `%boss_alias_plain%`: The Boss's alias stripped of color codes.
- `%boss_health%`: The Boss's current health.
- `%boss_location%`: The Boss's serialized location string.
- `%boss_location_x%`: The Boss's X block coordinate.
- `%boss_location_y%`: The Boss's Y block coordinate.
- `%boss_location_z%`: The Boss's Z block coordinate.
- `%boss_location_world%`: The Boss's world name.
- `%boss_top_damage_N%`: The Nth highest damage value dealt to the nearest Boss (1-based index, default 1).
- `%boss_top_damager_N%`: The name of the Nth top damager of the nearest Boss (1-based index, default 1).

#### Per-Boss Alias Placeholder
- `%boss_{bossName}_alias%`: Returns the alias of the named Boss.
- `%boss_{bossName}_alias_plain%`: Returns the alias of the named Boss without color codes.

#### Per-Boss Per-Player Statistics
- `%boss_{bossName}_player_kills%`: How many times the current player killed this Boss.
- `%boss_{bossName}_player_damage%`: Total damage the current player dealt to this Boss (formatted to 2 decimals).
- `%boss_{bossName}_{playerName}_kills%`: How many times a specific player killed this Boss (player must be online).
- `%boss_{bossName}_{playerName}_damage%`: Total damage a specific player dealt to this Boss.
- `%boss_{bossName}_{uuid}_kills%`: How many times a player (by UUID) killed this Boss.
- `%boss_{bossName}_{uuid}_damage%`: Total damage by UUID.

#### Per-Boss Top Statistics
- `%boss_{bossName}_top_kills_{order}_player%`: The player name at the given rank in kills leaderboard.
- `%boss_{bossName}_top_kills_{order}_value%`: The kill count at the given rank (returned as integer).
- `%boss_{bossName}_top_damage_{order}_player%`: The player name at the given rank in damage leaderboard.
- `%boss_{bossName}_top_damage_{order}_value%`: The damage value at the given rank (formatted to 2 decimals).

#### Per-Boss Respawn Countdown
- `%boss_{bossName}_respawn_{spawnRule}%`: Time until the Boss respawns from a RESPAWN_AFTER_DEATH spawn rule. Shows a formatted time string (e.g., `1m 30s`) or the `Respawn_Placeholder_Past_Due` value (default: `Spawned`) if the timer has expired or the Boss has never died.

#### Region Creation Placeholders
These track the player's in-progress region creation:
- `%boss_has_region%`: Whether the player has a complete region selected (localized yes/no).
- `%boss_region_primary_x%`: Primary point X coordinate.
- `%boss_region_primary_y%`: Primary point Y coordinate.
- `%boss_region_primary_z%`: Primary point Z coordinate.
- `%boss_region_secondary_x%`: Secondary point X coordinate.
- `%boss_region_secondary_y%`: Secondary point Y coordinate.
- `%boss_region_secondary_z%`: Secondary point Z coordinate.
- `%boss_region_world%`: The region's world name (or `region incomplete` if not fully set).
- `%boss_region_size%`: The number of blocks in the region (formatted with comma separators).

### Global Settings (settings.yml)

#### Command_Aliases
```yaml
Command_Aliases: [boss, b]
```
The first alias is the main command label. Additional entries are aliases. Do not remove the first entry.

#### Spawning Section
See the spawning SKILL.md for full details. Key settings: `Air_Spawn`, `Air_Spawn_Max_Distance`, `Ignore_Replacing_Vanilla_From`, `Cancel_Vanilla_If_Replace_Fails`, `Location_Spawn_Nearby_Player_Radius`, `Nearby_Spawn_Min_Distance_From_Player`, `Count_Unloaded_Bosses_In_Limits`, `Respawn_Placeholder_Past_Due`, `Live_Updates`, `Integration.Lands`.

#### Fighting Section
```yaml
Fighting:
  Retarget_Chance: 0%
  Disable_Cheats: [FLIGHT, GOD_MODE, INVISIBILITY]
  Health_Bar:
    Enabled: true
    Format: "&4{damage} dmg &8| &7{boss_alias}"
    Prefix: "&8["
    Suffix: "&8]"
    Color:
      Remaining: DARK_RED
      Total: GRAY
      Dead: BLACK
  Citizens_Retarget:
    Enabled: true
    Delay: 30 seconds
```
- **Retarget_Chance**: Percentage chance (0-100%) that hitting a Boss already targeting someone else makes it target you instead.
- **Disable_Cheats**: List of `BossCheatDisable` values. When a player attacks or is attacked by a Boss, these abilities are disabled. Options: FLIGHT, GOD_MODE, INVISIBILITY.
- **Health_Bar**: Action bar displayed when damaging a Boss. Variables in Format: `{damage}`, `{world}`, `{x}`, `{y}`, `{z}`, `{player}`, `{boss_alias}`. Colors use `CompChatColor` names.
- **Citizens_Retarget**: If Citizens plugin is installed, Boss NPCs periodically switch targets. Delay controls how often.

#### Health Section
```yaml
Health:
  Prevent_Regeneration: false
```
If true, prevents all Bosses from regenerating health from any source.

#### Death Section
```yaml
Death:
  Run_PvP_Commands_As_Console: true
```
Controls whether player drop commands run as the server console (true) or as the player (false).

#### Variables Section
```yaml
Variables:
  Nearby_Boss_Radius: 20
```
The maximum radius around the player to search for the closest Boss when resolving PlaceholderAPI variables that reference the nearest Boss.

#### Skills Section
```yaml
Skills:
  Target_Range: 8
```
Maximum distance from Boss to player for target-based skills to fire.

#### Other Root Settings
- **Timezone**: Java timezone ID for spawn rule day/month conditions (e.g., `Europe/Budapest`, `America/New_York`).
- **Sort_By_Type**: If true, the `/boss menu` GUI groups Bosses by entity type. If false, sorts A-Z. Requires restart.
- **Register_Regions**: Enable Boss regions for spawn rules and `/boss regions`. Requires restart when toggled.
- **Register_Tools**: Enable tool click detection for region/location creation. Disable for performance after setting up regions. Requires restart.
- **Locale**: Language file to use (default: `en_US`). Use `/boss dumplocale` to export for editing.
- **Prefix**: Chat message prefix. Available as `{prefix_plugin}` variable.
- **Log_Lag_Over_Milis**: Log operations exceeding this duration in milliseconds. Set to -1 to disable.
- **Notify_New_Versions**: Notify players with `boss.update.notify` permission about new versions.
- **Sentry**: Send anonymized error reports to sentry.io.
- **Debug**: List of debug sections to enable. Available: `spawning`, `skills`, `region-keep`, `unloaded`, `commands`, `health`.

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
- `src/main/java/org/mineacademy/boss/command/EggDropCommand.java` - /boss eggdrop command
- `src/main/java/org/mineacademy/boss/command/ButcherCommand.java` - /boss butcher command
- `src/main/java/org/mineacademy/boss/command/ListCommand.java` - /boss list command
- `src/main/java/org/mineacademy/boss/command/RemoveCommand.java` - /boss remove command
- `src/main/java/org/mineacademy/boss/command/FindCommand.java` - /boss find command
- `src/main/java/org/mineacademy/boss/command/ScanCommand.java` - /boss scan command
- `src/main/java/org/mineacademy/boss/command/LocationCommand.java` - /boss location command with sub-parameters
- `src/main/java/org/mineacademy/boss/command/UidCommand.java` - /boss uid command
- `src/main/java/org/mineacademy/boss/command/BiomeCommand.java` - /boss biome command
- `src/main/java/org/mineacademy/boss/command/SkullCommand.java` - /boss skull command
- `src/main/java/org/mineacademy/boss/command/CountUnloadedCommand.java` - /boss countunloaded command
- `src/main/java/org/mineacademy/boss/model/Permissions.java` - Permission definitions with annotations
- `src/main/java/org/mineacademy/boss/model/BossPlaceholders.java` - PlaceholderAPI expansion
- `src/main/java/org/mineacademy/boss/model/BossCheatDisable.java` - Cheat disable enum (FLIGHT, GOD_MODE, INVISIBILITY)
- `src/main/java/org/mineacademy/boss/settings/Settings.java` - Global settings loader
- `src/main/resources/settings.yml` - Default settings file
