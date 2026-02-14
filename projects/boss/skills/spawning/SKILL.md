---
name: boss-spawning
description: 'Spawn rules, conditions, limits, and automatic Boss spawning'
---

# Spawn Rules

## Overview

Spawn rules control how, when, and where Bosses automatically appear in the world. There are 5 rule types, each with shared conditions (days, months, time, light, weather, chance) and type-specific settings (locations, regions, radius, vanilla replacement). Rules are stored as YAML files in the `spawnrules/` folder and managed via `/boss menu` GUI or direct YAML editing.

## Architecture

### Key Classes

- `SpawnRule` (spawn/SpawnRule.java): Abstract base class extending `YamlConfig`. Holds shared fields: Type, Enabled, Bosses (whitelist), Delay, Days, Months, Minecraft_Time, Light_Level, Rain, Thunder, Chance, Last_Executed. Contains `canRun()` checks, `spawn()` execution, and the menu button system. The static `tick()` method iterates all rules of given types.
- `SpawnRuleType` (spawn/SpawnRuleType.java): Enum of 5 rule types, each mapping to its implementation class and providing an icon and description.
- `SpawnData` (spawn/SpawnData.java): Transferable data object passed between spawn rules during ticking. Contains a tag-based data map (LOCATION, MATCHING_TYPE, REGION) and a list of successfully spawned Bosses. Factory methods: `fromVanillaReplace()`, `fromRegionEnter()`, `fromBehaviorTask()`.
- `SpawnRuleLocationPeriod` (spawn/SpawnRuleLocationPeriod.java): Extends `SpawnRuleLocationData`. Spawns at configured locations on a timer.
- `SpawnRuleRespawn` (spawn/SpawnRuleRespawn.java): Extends `SpawnRuleLocationData`. Spawns at configured locations after the previous Boss from this rule dies. Uses `Boss.getLastDeathFromSpawnRule()` to track death timestamps. Checks that no other Boss from this rule is currently alive.
- `SpawnRuleRegionEnter` (spawn/SpawnRuleRegionEnter.java): Extends `SpawnRuleRegions`. Triggered when a player enters a Boss region. Spawns at configured locations within the region. Has `Max_Bosses_In_Region` limit.
- `SpawnRuleRandomPeriod` (spawn/SpawnRuleRandomPeriod.java): Extends `SpawnRuleRandom`. Spawns randomly around online players within a `Block_Radius`. Finds a random XZ offset from each player, resolves Y coordinate (handles Nether), and spawns. Respects `Nearby_Spawn_Min_Distance_From_Player` from settings.yml. Avoids GriefPrevention claims.
- `SpawnRuleRandomVanilla` (spawn/SpawnRuleRandomVanilla.java): Extends `SpawnRuleRandom`. Replaces vanilla mob spawns. When a vanilla entity spawns, checks if the Boss list has a matching entity type and replaces it.
- `SpawnRuleLocationData` (spawn/SpawnRuleLocationData.java): Abstract class for location-based rules. Manages a set of `BossLocation` names where Bosses should spawn. Checks `Location_Spawn_Nearby_Player_Radius` to ensure a player is nearby.
- `SpawnRuleRegions` (spawn/SpawnRuleRegions.java): Abstract class for region-aware rules. Manages region whitelists/blacklists with spawn chances per region.
- `SpawnRuleRandom` (spawn/SpawnRuleRandom.java): Abstract class for rules that have region and world filtering.
- `TaskBehavior` (task/TaskBehavior.java): Runnable task that ticks LOCATION_PERIOD, RESPAWN_AFTER_DEATH, and PERIOD rules every second. Also handles skill execution for nearby Bosses.
- `TaskRegionEnter` (task/TaskRegionEnter.java): Runnable task that checks if players entered Boss regions and ticks REGION_ENTER rules.

### How Spawn Rules Execute

1. `TaskBehavior` runs every 20 ticks (1 second). It calls `SpawnRule.tick(data, LOCATION_PERIOD, RESPAWN_AFTER_DEATH, PERIOD)`.
2. `TaskRegionEnter` runs every 20 ticks. For each online player, it checks if they entered a DiskRegion and calls `SpawnRule.tick(data, REGION_ENTER)`.
3. For REPLACE_VANILLA, the `EntityListener` intercepts `CreatureSpawnEvent`, creates `SpawnData.fromVanillaReplace()`, and ticks rules.
4. Each rule's `onTick()` calls `canRun()` (global conditions), then `canRun(location)` (location conditions), then `spawn()`.
5. `spawn()` iterates all Boss objects, checking if the Boss is in the rule's Bosses list and matching entity type, then calls `Boss.spawn()`.

## Configuration

### 5 Spawn Rule Types

#### LOCATION_PERIOD
Spawns Bosses at specific saved locations on a repeating timer.
- Set locations using the GUI (click to add BossLocations).
- Delay controls how often the rule runs.
- Requires a player within `Location_Spawn_Nearby_Player_Radius` blocks (settings.yml, default 30, -1 to disable).

#### RESPAWN_AFTER_DEATH
Spawns the next Boss at configured locations after the previous one from this rule is killed.
- Delay controls the wait time after death before respawning.
- Only one Boss from this rule can be alive at a time.
- Tracks death timestamps per Boss per spawn rule via `Last_Death_From_Spawn_Rule` in Boss YAML.
- The `%boss_{bossName}_respawn_{spawnRule}%` placeholder shows countdown until respawn.

#### REGION_ENTER
Spawns Bosses when a player enters a Boss region.
- Requires Boss regions to be set up (`Register_Regions: true` in settings.yml).
- Configure which regions trigger the rule.
- Set spawn locations within the region.
- `Max_Bosses_In_Region` limits how many Bosses of this rule can exist in a region simultaneously.

#### PERIOD
Spawns Bosses randomly around online players on a timer.
- `Block_Radius` (5-80, default 30) controls the spawn radius around each player.
- Finds a random XZ offset, resolves safe Y coordinate (handles Nether with ceiling check).
- Respects `Nearby_Spawn_Min_Distance_From_Player` (settings.yml, default 5 blocks).
- Avoids GriefPrevention claims.

#### REPLACE_VANILLA
Replaces vanilla mob spawns with Bosses of matching entity type.
- Only replaces mobs whose EntityType matches a Boss in the rule's list.
- `Ignore_Replacing_Vanilla_From` (settings.yml) excludes certain SpawnReasons (default: COMMAND, CUSTOM, SLIME_SPLIT).
- `Cancel_Vanilla_If_Replace_Fails` (settings.yml) prevents the vanilla mob from spawning if replacement fails.

### Shared Spawn Rule Settings

All rules share these configurable fields:

```yaml
Type: LOCATION_PERIOD
Enabled: true
Bosses: ["*"]
Delay: "30 seconds"
Days: ["*"]
Months: ["*"]
Minecraft_Time: "0 - 12000"
Light_Level: "0 - 7"
Rain: false
Thunder: false
Chance: 1.0
Last_Executed: -1
```

### Conditions

- **Bosses**: Whitelist of Boss names this rule applies to. Use `["*"]` for all Bosses.
- **Delay**: Time between rule executions. Format: `30 seconds`, `5 minutes`, `1 hour`. For RESPAWN_AFTER_DEATH, this is the delay after death. Default: 0 (every tick for periodic rules, defaults to 1 second minimum).
- **Days**: Real-life days of the week. Values: MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY. Use `["*"]` for all days.
- **Months**: Real-life months. Values: JANUARY through DECEMBER. Use `["*"]` for all months.
- **Minecraft_Time**: In-game tick range (0-24000). `0 - 12000` = daytime, `12000 - 24000` = nighttime. Set to null for any time. The Timezone setting in settings.yml affects real-life day/month checks.
- **Light_Level**: Block light level range (0-15). Useful for spawning in dark areas. Set to null for all levels.
- **Rain**: If true, rule only fires during rain/storm.
- **Thunder**: If true, rule only fires during thunderstorms.
- **Chance**: Probability (0.0-1.0) that the rule executes when checked. 1.0 = always, 0.5 = 50%.

### Spawning Limits

Limits are configured per-Boss (in the Boss YAML), not per-rule:

- **Limit.Nearby_Bosses**: `Key` = max count, `Value` = radius in blocks. If there are already this many of the same Boss within the radius, spawning is denied.
- **Limit.Worlds**: Map of world name to max count. Prevents more than N of this Boss in a world.
- **Limit_Reasons**: Which `BossSpawnReason` values trigger limit checks. Default: `[SPAWN_RULE]`. Options: COMMAND, SPAWN_RULE, RIDING, REINFORCEMENTS, EGG, API.
- **Count_Unloaded_Bosses_In_Limits** (settings.yml): If true and running Paper, counts Bosses in unloaded chunks toward limits via `unloaded-bosses.xml`.

### Prevent Vanilla Mobs (settings.yml)

A separate feature (not a spawn rule) that blocks vanilla mobs entirely:

```yaml
Prevent_Vanilla_Mobs:
  Enabled: false
  Prevent_From: [NATURAL, CHUNK_GEN, SPAWNER, VILLAGE_DEFENSE, VILLAGE_INVASION, REINFORCEMENTS, INFECTION, CURED, DROWNED]
  Entities: ["*"]
  Worlds: ["*"]
```

Set `Entities` to specific types or `["*"]` for all. Works independently from Boss spawn rules.

### Spawning Settings (settings.yml)

```yaml
Spawning:
  Air_Spawn: true
  Air_Spawn_Max_Distance: 30
  Ignore_Replacing_Vanilla_From: [COMMAND, CUSTOM, SLIME_SPLIT]
  Cancel_Vanilla_If_Replace_Fails: false
  Location_Spawn_Nearby_Player_Radius: 30
  Nearby_Spawn_Min_Distance_From_Player: 5
  Count_Unloaded_Bosses_In_Limits: true
  Respawn_Placeholder_Past_Due: "Spawned"
  Live_Updates: true
  Integration:
    Lands: true
```

- **Air_Spawn**: Allow right-clicking air with Boss egg to spawn at distance.
- **Air_Spawn_Max_Distance**: How far away the Boss spawns when air-spawning. Do not set to 0 or -1 (use Air_Spawn: false instead).
- **Location_Spawn_Nearby_Player_Radius**: Location-based rules only run when a player is within this radius. -1 to disable.
- **Lands**: Respect Lands plugin mob/animal/phantom flags.
- **Live_Updates**: When Boss settings change via GUI, update all alive Bosses of that type immediately.

## Common Issues & Solutions

- **Bosses not spawning from rules**: Set `Debug: [spawning]` in settings.yml and check console output. Common causes: no player nearby (Location_Spawn_Nearby_Player_Radius), delay not elapsed, conditions not met (wrong day/month/time/light/weather), chance did not pass, limits exceeded, chunk unloaded, Lands flag blocking.
- **RESPAWN_AFTER_DEATH not working**: Ensure only one Boss of this rule should be alive at a time. The rule checks all alive Bosses for its spawn rule tag. The Delay is measured from the moment the previous Boss died. If the Boss was killed before the plugin tracked it (e.g., during shutdown), the death may not be recorded.
- **REPLACE_VANILLA not replacing**: Check `Ignore_Replacing_Vanilla_From` in settings.yml. The spawn cause must not be in the ignore list. The Boss list must contain a Boss with the same EntityType as the vanilla mob. Verify with debug mode.
- **PERIOD spawning too many Bosses**: Reduce Chance, increase Delay, or tighten Limit.Nearby_Bosses in the Boss YAML. Each online player triggers a spawn check, so more players = more spawns.
- **REGION_ENTER not triggering**: Ensure `Register_Regions: true` in settings.yml (requires server restart when toggled). The player must enter a Boss region that is assigned to the rule. Check that locations are configured and valid.
- **Timezone issues**: Set the `Timezone` key in settings.yml (e.g., `Europe/Budapest`, `America/New_York`). This affects Days and Months conditions.
- **Unloaded Boss counting not working**: `Count_Unloaded_Bosses_In_Limits` requires Paper server. On Spigot, it is automatically disabled.

## Key File Paths

- `src/main/java/org/mineacademy/boss/spawn/SpawnRule.java` - Base spawn rule class with shared conditions
- `src/main/java/org/mineacademy/boss/spawn/SpawnRuleType.java` - 5 rule type enum
- `src/main/java/org/mineacademy/boss/spawn/SpawnData.java` - Data transfer object for spawn context
- `src/main/java/org/mineacademy/boss/spawn/SpawnRuleLocationPeriod.java` - LOCATION_PERIOD implementation
- `src/main/java/org/mineacademy/boss/spawn/SpawnRuleRespawn.java` - RESPAWN_AFTER_DEATH implementation
- `src/main/java/org/mineacademy/boss/spawn/SpawnRuleRegionEnter.java` - REGION_ENTER implementation
- `src/main/java/org/mineacademy/boss/spawn/SpawnRuleRandomPeriod.java` - PERIOD implementation
- `src/main/java/org/mineacademy/boss/spawn/SpawnRuleRandomVanilla.java` - REPLACE_VANILLA implementation
- `src/main/java/org/mineacademy/boss/spawn/SpawnRuleLocationData.java` - Location-based rule base class
- `src/main/java/org/mineacademy/boss/spawn/SpawnRuleRegions.java` - Region-aware rule base class
- `src/main/java/org/mineacademy/boss/spawn/SpawnRuleRandom.java` - Random/vanilla rule base class
- `src/main/java/org/mineacademy/boss/task/TaskBehavior.java` - Main tick task for periodic rules
- `src/main/java/org/mineacademy/boss/task/TaskRegionEnter.java` - Region enter detection task
- `src/main/java/org/mineacademy/boss/listener/ChunkListener.java` - Unloaded Boss tracking
- `src/main/java/org/mineacademy/boss/settings/Settings.java` - Spawning settings
- `src/main/resources/settings.yml` - Default settings with spawning section
