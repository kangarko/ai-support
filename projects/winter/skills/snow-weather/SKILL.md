---
name: snow-weather
description: 'Snow particles, terrain snow generation, weather control, and biome disguising'
---

# Snow, Terrain & Weather

## Overview

Winter provides three layered systems for winter effects: visual snow particles (cosmetic only), terrain snow generation (actual block changes), and weather control. An optional biome disguise system uses ProtocolLib to make all biomes appear as cold/snowy biomes client-side without modifying the world.

## Architecture

### Key Classes

- `TaskParticleSnow` -- Repeating task that spawns FIREWORKS_SPARK particles around each online player. Runs every `Snow.Period_Ticks` ticks. Contains an inner `ParticleLimiter` class that checks server TPS every 20 seconds and reduces particle count to 8 when TPS drops below 17.
- `TaskTerrain` -- Repeating task that places or removes snow blocks in chunks near players. Runs every `Terrain.Snow_Generation.Period_Ticks` ticks. Loads chunks within the configured radius of each player, picks random non-snow locations in each chunk, and either places snow layers or melts existing ones depending on the `Melt` flag. Handles multi-layer snow growth using neighbor checks, crop destruction, water freezing, and snow-block conversion.
- `TaskWeather` -- Repeating task (every 3 seconds) that either disables weather entirely or tracks thunderstorms for the snow storm effect via `SnowStorm` model.
- `SnowStorm` -- Static set tracking which worlds currently have a thunderstorm active. When a world is storming, `TaskParticleSnow` sets particle speed to 1 (chaotic movement) instead of the configured `Chaos` value.
- `ProtocolLibBiomeHook` -- Intercepts MAP_CHUNK packets via ProtocolLib and rewrites biome data to the configured cold biome ID. Has version-specific remapper classes: `Remapper1_8_8`, `REmapper1_7_10`, `REmapper1_11_and_12`, `REmapper1_13_to_1_17`.
- `MeltingListener` -- Cancels `BlockFadeEvent` for materials listed in `Terrain.Prevent_Melting`.
- `WinterListener` -- Cancels `WeatherChangeEvent` when `Weather.Disable` is true. Also handles `RegionScanCompleteEvent` for the populate command.
- `WinterUtil` -- Utility methods: `canMelt()` checks if a location's biome is naturally snowy (respects `Only_Melt_Unnatural_Snow`), `canPlace()` validates a ground block against `Do_Not_Place_On`, `isInRegion()` checks WorldGuard regions via `Whiteblacklist`, `nextLocationNoSnow()` picks a random non-snow location in a chunk.
- `FreezeIgnore` -- Model that prevents water freezing near certain neighbor block + crop combinations.
- `PlayerData` -- Stores per-player snow toggle state in `Snow_Disabled` list in data.yml. `hasSnowEnabled()` returns true unless the player's UUID is in the disabled set.

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

## Configuration

All settings are in `settings.yml`.

### Snow (Particles)

```yaml
Snow:
  Enabled: true                   # Master toggle for snow particles
  Period_Ticks: 3                 # Spawn interval (20 ticks = 1 second), lower = more frequent
  Amount: 40                      # Particles per player per tick cycle
  Chaos: 0.0                      # Random bounce intensity, 0.8 for storm-like effect
  Realistic: true                 # Only spawn in open sky (not under roofs)
  Require_Snow_Biomes: false      # Restrict to cold/ice/frozen biomes and high altitude
  Ignore_Vanished: true           # Skip vanished and spectator players
  Range:
    Horizontal: 15                # X-Z radius in blocks
    Vertical: 15                  # Y radius in blocks
  Regions:
    Enabled: false                # Enable WorldGuard region filtering
    List: []                      # Whitelist by default, prefix @blacklist to invert
```

### Terrain.Snow_Generation

```yaml
Terrain:
  Prevent_Melting: [ICE, SNOW_BLOCK, SNOW]   # Cancel BlockFadeEvent for these materials

  Snow_Generation:                             # DOES NOT SUPPORT /WINTER RELOAD
    Enabled: false                             # Place/remove snow blocks around players
    Melt: false                                # Reverse mode: remove snow instead of placing
    Only_Melt_Unnatural_Snow: true             # Skip naturally snowy biomes when melting
    Melt_Snow_Block_To_Snow_Layer: false        # Convert snow blocks to layers before melting
    Freeze_Water: true                         # Convert water to ice (or ice to water when melting)
    Destroy_Crops: false                       # Place snow on farmland, destroying crops
    Freeze_Ignore:                             # Prevent freezing near specific neighbor+crop combos
      "SAND, GRASS, DIRT": "SUGAR_CANE, SUGAR_CANE_BLOCK"
      "SAND": "CACTUS"
      "SOIL": "*"
    Period_Ticks: 40                           # How often to scan for blocks (20 ticks = 1 second)
    Radius: 3                                  # Chunk radius around each player (approx. radius*15 blocks)
    Multi_Layer: true                          # Allow snow to stack multiple layers
    Required_Neighbors_To_Grow: 2              # Side blocks at same level needed for layer growth
    Convert_Full_Snow_To_Snow_Block: false     # Convert 8-layer snow to snow block
    Max_Snow_Layers_Height: 3                  # Max snow layers (1 block = 8 layers)
    Do_Not_Place_On: [AIR, ANVIL, TABLE, ...]  # Material substrings to exclude
    Ignore_Biomes: []                          # Biome names to skip
    Regions:
      Enabled: false                           # Enable WorldGuard region filtering
      List: []                                 # Whitelist by default, prefix @blacklist to invert
```

### Terrain.Disguise_Biomes

```yaml
Terrain:
  Disguise_Biomes:
    Enabled: false                # Disguise all biomes as a cold biome (client-side only)
    Biome: ICE_MOUNTAINS          # Target biome name
```

Requires ProtocolLib. Only works on MC 1.7.10, 1.8.8, 1.11, 1.12, 1.16, and 1.17. Does not modify the actual world -- purely packet-level visual change.

### Weather

```yaml
Weather:
  Disable: false      # Completely prevent rain/thunderstorm (disables Snow_Storm)
  Snow_Storm: true    # Make particles chaotic during thunderstorms
```

### Worlds

```yaml
Worlds:
  - '*'               # List of enabled worlds, or '*' for all
```

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
- Snow storm model: `src/main/java/org/mineacademy/winter/model/SnowStorm.java`
- Freeze ignore model: `src/main/java/org/mineacademy/winter/model/FreezeIgnore.java`
- Utility: `src/main/java/org/mineacademy/winter/util/WinterUtil.java`
- Player data (snow toggle): `src/main/java/org/mineacademy/winter/model/PlayerData.java`
- Plugin bootstrap: `src/main/java/org/mineacademy/winter/WinterPlugin.java`
