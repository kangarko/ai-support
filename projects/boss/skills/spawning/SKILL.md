---
name: boss-spawning
description: 'Spawn rules, conditions, limits, and automatic Boss spawning'
---

# Spawn Rules

## Overview

Spawn rules control how, when, and where Bosses automatically appear in the world. There are 5 rule types, each with shared conditions (days, months, time, light, weather, chance) and type-specific settings (locations, regions, radius, vanilla replacement). Rules are stored as YAML files in the `spawnrules/` folder and managed via `/boss menu` GUI or direct YAML editing.

## Architecture

### Key Classes

- `SpawnRule` (spawn/SpawnRule.java): Abstract base class extending `YamlConfig`.
- `SpawnRuleType` (spawn/SpawnRuleType.java): Enum of 5 rule types, each mapping to its implementation class and providing an icon and description.
- `SpawnData` (spawn/SpawnData.java): Transferable data object passed between spawn rules during ticking.
- `SpawnRuleLocationPeriod` (spawn/SpawnRuleLocationPeriod.java): Extends `SpawnRuleLocationData`.
- `SpawnRuleRespawn` (spawn/SpawnRuleRespawn.java): Extends `SpawnRuleLocationData`.
- `SpawnRuleRegionEnter` (spawn/SpawnRuleRegionEnter.java): Extends `SpawnRuleRegions`.
- `SpawnRuleRandomPeriod` (spawn/SpawnRuleRandomPeriod.java): Extends `SpawnRuleRandom`.
- `SpawnRuleRandomVanilla` (spawn/SpawnRuleRandomVanilla.java): Extends `SpawnRuleRandom`.
- `SpawnRuleLocationData` (spawn/SpawnRuleLocationData.java): Abstract class for location-based rules.
- `SpawnRuleRegions` (spawn/SpawnRuleRegions.java): Abstract class for region-aware rules.
- `SpawnRuleRandom` (spawn/SpawnRuleRandom.java): Abstract class for rules that have region and world filtering.
- `TaskBehavior` (task/TaskBehavior.java): Runnable task that ticks LOCATION_PERIOD, RESPAWN_AFTER_DEATH, and PERIOD rules every second.
- `TaskRegionEnter` (task/TaskRegionEnter.java): Runnable task that checks if players entered Boss regions and ticks REGION_ENTER rules.

### How Spawn Rules Execute

1. `TaskBehavior` runs every 20 ticks (1 second). It calls `SpawnRule.tick(data, LOCATION_PERIOD, RESPAWN_AFTER_DEATH, PERIOD)`.
2. `TaskRegionEnter` runs every 20 ticks. For each online player, it checks if they entered a DiskRegion and calls `SpawnRule.tick(data, REGION_ENTER)`.
3. For REPLACE_VANILLA, the `EntityListener` intercepts `CreatureSpawnEvent`, creates `SpawnData.fromVanillaReplace()`, and ticks rules.
4. Each rule's `onTick()` calls `canRun()` (global conditions), then `canRun(location)` (location conditions), then `spawn()`.
5. `spawn()` iterates all Boss objects, checking if the Boss is in the rule's Bosses list and matching entity type, then calls `Boss.spawn()`.

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

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
