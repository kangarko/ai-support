---
name: snow-weather
description: 'Snow particles, terrain snow generation, weather control, and biome disguising'
---

# Snow, Terrain & Weather

## Overview

Winter provides three layered systems for winter effects: visual snow particles (cosmetic only), terrain snow generation (actual block changes), and weather control. An optional biome disguise system uses ProtocolLib to make all biomes appear as cold/snowy biomes client-side without modifying the world.

## Architecture

### Key Classes

- `TaskParticleSnow` -- Repeating task that spawns FIREWORKS_SPARK particles around each online player.
- `TaskTerrain` -- Repeating task that places or removes snow blocks in chunks near players.
- `TaskWeather` -- Repeating task (every 3 seconds) that either disables weather entirely or tracks thunderstorms for the snow storm effect via `SnowStorm` model.
- `SnowStorm` -- Static set tracking which worlds currently have a thunderstorm active.
- `ProtocolLibBiomeHook` -- Intercepts MAP_CHUNK packets via ProtocolLib and rewrites biome data to the configured cold biome ID.
- `MeltingListener` -- Cancels `BlockFadeEvent` for materials listed in `Terrain.Prevent_Melting`.
- `WinterListener` -- Cancels `WeatherChangeEvent` when `Weather.Disable` is true.
- `WinterUtil` -- Utility methods: `canMelt()` checks if a location's biome is naturally snowy (respects `Only_Melt_Unnatural_Snow`), `canPlace()` validates a ground block against `Do_Not_Place_On`, `isInRegion()` checks WorldGuard regions via `Whiteblacklist`, `nextLocationNoSnow()` picks a random non-snow location in a chunk.
- `FreezeIgnore` -- Model that prevents water freezing near certain neighbor block + crop combinations.
- `PlayerData` -- Stores per-player snow toggle state in `Snow_Disabled` list in data.yml.

### Task Registration (WinterPlugin.onPluginStart)

- `TaskParticleSnow` starts if `Snow.Enabled` is true.
- `TaskTerrain` starts if `Terrain.Snow_Generation.Enabled` is true.
- `TaskWeather` starts if `Weather.Disable` or `Weather.Snow_Storm` is true.
- `MeltingListener` registers if `Terrain.Prevent_Melting` is non-empty.
- `ProtocolLibBiomeHook` initializes if `Terrain.Disguise_Biomes.Enabled` is true and ProtocolLib is loaded.

### Particle Flow

1. Every `Period_Ticks`, iterate all online players.
2. Skip players not in allowed worlds, with snow disabled, or vanished/spectator (if `Ignore_Vanished` is true).
3. For each player, determine particle speed: 1 during snow storms, otherwise `Chaos` value.
4. Spawn `Amount` particles (reduced to 8 on low TPS) at random locations within `Range.Horizontal` / `Range.Vertical` of the player.
5. Each random location is validated: must be in a snow biome if `Require_Snow_Biomes` is true, must be in a whitelisted WorldGuard region if `Regions.Enabled` is true, must be under open sky if `Realistic` is true, and the block + block below must both be air.

### Terrain Snow Flow

1. Every `Period_Ticks`, load chunks within `Radius` of each player in allowed worlds.
2. For each chunk, pick a random non-snow location.
3. Check biome against `Ignore_Biomes` and region against `Regions` list.
4. If `Melt` is false (snow placement mode): place snow on valid ground, grow existing snow layers if neighbors meet `Required_Neighbors_To_Grow` threshold and `Multi_Layer` is true, convert full 8-layer snow to snow block if `Convert_Full_Snow_To_Snow_Block` is true, cap at `Max_Snow_Layers_Height`.
5. If `Melt` is true: reduce snow layers, respecting `Only_Melt_Unnatural_Snow` (skips naturally snowy biomes and Y>90 mountain biomes). Convert ice back to water if `Freeze_Water` is true. Optionally convert snow blocks to 7-layer snow first if `Melt_Snow_Block_To_Snow_Layer` is true.
6. `Destroy_Crops`: if the block two below is farmland, place snow and convert farmland to dirt.
7. `Freeze_Water`: freeze water to ice (or thaw ice to water when melting), respecting `Freeze_Ignore` rules that prevent freezing near certain neighbor blocks with specific crops.

## Common Issues & Solutions

| Issue | Cause | Solution |
|---|---|---|
| Particles not showing | `Snow.Enabled` is false, or player toggled off via `/winter snow` | Check settings and run `/winter snow` to re-enable |
| Particles only in certain areas | `Require_Snow_Biomes: true` or `Regions.Enabled: true` | Set `Require_Snow_Biomes: false` or configure region list |
| No particles under roofs/caves | `Realistic: true` blocks indoor particles | Set `Realistic: false` to allow particles everywhere |
| Snow blocks not generating | `Terrain.Snow_Generation.Enabled: false` (disabled by default) | Set to `true` and restart (does not support `/winter reload`) |
| Snow not melting | `Melt: false` or `Only_Melt_Unnatural_Snow: true` blocks natural biomes | Set `Melt: true` and check biome settings |
| Biome disguise not working | Missing ProtocolLib or unsupported MC version | Install ProtocolLib, use MC 1.7.10/1.8.8/1.11/1.12/1.16/1.17 |
| Snow_Generation changes ignored after reload | Terrain settings require full restart | Restart the server instead of using `/winter reload` |
| Performance degradation | High `Amount`, low `Period_Ticks`, high `Range`, high `Radius` | Reduce values. Use `Debug: [lag-particle]` to measure particle render time, aim for <1.5ms |
| Snow placed on unwanted blocks | Material not in `Do_Not_Place_On` list | Add the material substring to the list |
| Water freezing near crops | `Freeze_Ignore` not configured for that crop | Add the neighbor block and crop to `Freeze_Ignore` map |
| Weather still changing | `Weather.Disable: false` | Set to `true` to fully prevent weather changes |
| Snow storm effect not working | `Weather.Disable: true` overrides `Snow_Storm` | Set `Weather.Disable: false` and `Snow_Storm: true` |

## Key File Paths

- Settings: `src/main/resources/settings.yml` (Snow, Terrain, Weather, Worlds sections)
- Settings model: `src/main/java/org/mineacademy/winter/settings/Settings.java` (inner classes `Snow`, `Terrain`, `Weather`)
- Particle task: `src/main/java/org/mineacademy/winter/task/TaskParticleSnow.java`
- Terrain task: `src/main/java/org/mineacademy/winter/task/TaskTerrain.java`
- Weather task: `src/main/java/org/mineacademy/winter/task/TaskWeather.java`
- Biome hook: `src/main/java/org/mineacademy/winter/hook/ProtocolLibBiomeHook.java`
- Melting listener: `src/main/java/org/mineacademy/winter/listener/MeltingListener.java`
- Weather listener: `src/main/java/org/mineacademy/winter/listener/WinterListener.java`

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
