---
name: snowmen
description: 'Snowman protection, damage, Psycho hostile snowmen, and mob-to-snowman transformation'
---

# Snowman Features

## Overview

Winter enhances Minecraft snowmen with four systems: melt damage prevention, monster targeting prevention, snowball damage dealing, and mob-to-snowman transformation. An experimental Psycho system replaces normal snowmen with hostile NMS-level custom entities that actively attack players using melee and ranged attacks with custom sounds.

## Architecture

### Key Classes

- `SnowmanDamageListener` -- Cancels `EntityDamageEvent` with `DamageCause.MELTING` for snowmen when `Snowman.Enabled` and `Snowman.Disable_Melt_Damage` are both true. Only registered if both settings are true at startup.
- `SnowmanTargetListener` -- Cancels `EntityTargetLivingEntityEvent` when the target is a snowman and `Snowman.Prevent_Target` is true. Prevents zombies and other mobs from attacking snowmen. Only registered if `Snowman.Enabled` and `Snowman.Prevent_Target` are true.
- `SnowmanDealDamageListener` -- Two-part listener. On `ProjectileLaunchEvent`: if a snowball's shooter is a snowman, stores the snowball's UUID. On `ProjectileHitEvent`: if the snowball UUID is stored, deals `Snowman.Damage.Snowball` damage to the hit entity. Handles player blocking (shield) by playing a snow step sound instead of dealing damage. Only registered if `Snowman.Enabled` and `Snowman.Damage.Snowball > 0`.
- `SnowmanTransformListener` -- On `CreatureSpawnEvent`: if the spawning entity type is in `Snowman.Transform.Applicable` and a random roll succeeds (`Chance_Percent`), cancels the spawn and spawns a vanilla snowman instead. Only registered if `Snowman.Enabled` and `Snowman.Transform.Enabled` are true.
- `PsychoMob` -- Listener and factory for hostile snowmen. Handles two events: `CreatureSpawnEvent` converts newly spawned snowmen to Psycho (if `Convert_New` is true and entity lacks `DeadlySnowman` metadata), and `ChunkLoadEvent` converts existing snowmen in loaded chunks (if `Convert_Existing` is true). Static `spawn(Location)` dispatches to the correct version-specific implementation. Only registered if `PsychoMob.IS_COMPATIBLE` is true.
- `PsychoMobModern` -- NMS snowman for MC 1.20.5+. Extends `net.minecraft.world.entity.animal.golem.SnowGolem`. Adds `MeleeAttackGoal` and `NearestAttackableTargetGoal<Player>` to make it hostile to players. Custom sounds: witch ambient, wither skeleton hurt/death. Removes pumpkin head unless `Pumpkin_Head` is true. Sets `persist` based on `Despawn` setting. Tags entity with `DeadlySnowman` metadata.
- `PsychoMob1_16` -- NMS snowman for MC 1.16.x.
- `PsychoMob1_12` -- NMS snowman for MC 1.12.x. Requires one-time `register()` call.
- `PsychoMob1_8` -- NMS snowman for MC 1.8.8. Requires one-time `register()` call.

### Version Compatibility

Psycho mob is compatible with: MC 1.8.8, 1.12, 1.16, 1.20.5+. The `IS_COMPATIBLE` static flag is computed at class load time. Cauldron servers are explicitly excluded. When `Convert_New` or `Convert_Existing` is enabled on an incompatible version, a warning is logged: "Psycho is not compatible with your MC version."

### Registration (WinterPlugin.onPluginStart)

All snowman listeners are conditionally registered based on settings:

- `PsychoMob` listener: registered if `PsychoMob.IS_COMPATIBLE` is true (regardless of Psycho settings, since `Convert_New`/`Convert_Existing` can be changed at runtime).
- `SnowmanDamageListener`: registered if `Snowman.Enabled` AND `Snowman.Disable_Melt_Damage` are true.
- `SnowmanDealDamageListener`: registered if `Snowman.Enabled` AND `Snowman.Damage.Snowball > 0`.
- `SnowmanTargetListener`: registered if `Snowman.Enabled` AND `Snowman.Prevent_Target` are true.
- `SnowmanTransformListener`: registered if `Snowman.Enabled` AND `Snowman.Transform.Enabled` are true.

## Configuration

All settings are in `settings.yml` under the `Snowman` section.

```yaml
Snowman:
  Enabled: true                  # Master toggle for all snowman behavior
  Disable_Melt_Damage: true      # Prevent snowmen from taking damage in warm biomes
  Prevent_Target: true           # Stop monsters from targeting/attacking snowmen

  Damage:
    Snowball: 3.0                # Damage dealt by snowman snowballs (0 to disable)

  Psycho:
    Convert_New: false           # Replace newly spawned snowmen with hostile Psycho
    Convert_Existing: false      # Replace existing snowmen in loaded chunks (IRREVERSIBLE)
    Pumpkin_Head: false           # Show pumpkin on Psycho head (false for cooler look)
    Despawn: true                # Allow Psycho to despawn when far away

  Transform:
    Enabled: true                # Convert spawned monsters to passive snowmen
    Chance_Percent: 15           # Percentage chance (0-100) for conversion
    Applicable: [ZOMBIE]         # Entity types eligible for conversion
```

### Key Setting Details

- `Enabled: false` disables all snowman features globally. Individual sub-features (melt damage, targeting, damage, transform) also have their own toggles checked in addition to the master toggle.
- `Psycho.Convert_Existing: true` is irreversible. Once a chunk is loaded and existing snowmen are converted, they become permanent Psycho entities. The original snowmen are removed via `entity.remove()` before spawning the Psycho replacement.
- `Psycho.Despawn: true` means the NMS entity has `persist = false`, allowing vanilla despawn mechanics. Set to `false` to make Psycho snowmen permanent.
- `Transform.Applicable` accepts any `EntityType` name from the Bukkit API. Invalid names are logged as warnings and skipped.
- `Damage.Snowball` uses direct health manipulation (`setHealth()`), not Bukkit damage events. This means armor does not reduce the damage. Player blocking (shield) negates the hit entirely.

### Commands

| Command | Permission | Description |
|---|---|---|
| `/winter psycho` (alias: `/winter ps`) | `winter.command.psycho` | Spawns a Psycho snowman at the player's location. Player-only command. Fails with error message if MC version is incompatible. |

## Common Issues & Solutions

| Issue | Cause | Solution |
|---|---|---|
| Snowmen still melting in desert | `Snowman.Enabled: false` or `Disable_Melt_Damage: false` | Enable both settings |
| Zombies still attacking snowmen | `Prevent_Target: false` or `Snowman.Enabled: false` | Enable both settings |
| Snowballs don't deal damage | `Damage.Snowball: 0` or `Snowman.Enabled: false` | Set `Snowball` to a positive value (e.g. 3.0) |
| Psycho not spawning | Incompatible MC version | Must be MC 1.8.8, 1.12, 1.16, or 1.20.5+. Check console for compatibility warning |
| `/winter psycho` error | Server is Cauldron/incompatible | Cauldron is explicitly excluded. Use Paper/Spigot/Purpur |
| Psycho not converting new snowmen | `Convert_New: false` | Set to `true`. The PsychoMob listener must be registered (requires compatible MC version) |
| Can't undo Convert_Existing | By design, this is irreversible | Restore from world backup taken before enabling |
| Transform not working | `Transform.Enabled: false` or entity type not in `Applicable` | Enable and add desired entity types to the list |
| Transform never triggers | `Chance_Percent` too low | Increase the percentage (0-100) |
| Psycho has pumpkin head | `Pumpkin_Head: true` | Set to `false` for the default bare head look |
| Psycho disappears | `Despawn: true` allows vanilla despawn | Set `Despawn: false` for permanent Psycho |
| Plugin won't load on Folia/Luminol | Unsupported platform | Use Paper, Spigot, or Purpur instead |

## Key File Paths

- Settings: `src/main/resources/settings.yml` (Snowman section)
- Settings model: `src/main/java/org/mineacademy/winter/settings/Settings.java` (inner class `Snowman`, sub-classes `Psycho`, `Damage`, `Transform`)
- Melt damage listener: `src/main/java/org/mineacademy/winter/listener/SnowmanDamageListener.java`
- Snowball damage listener: `src/main/java/org/mineacademy/winter/listener/SnowmanDealDamageListener.java`
- Target listener: `src/main/java/org/mineacademy/winter/listener/SnowmanTargetListener.java`
- Transform listener: `src/main/java/org/mineacademy/winter/listener/SnowmanTransformListener.java`
- Psycho factory/listener: `src/main/java/org/mineacademy/winter/psycho/PsychoMob.java`
- Psycho modern (1.20.5+): `src/main/java/org/mineacademy/winter/psycho/PsychoMobModern.java`
- Psycho 1.16: `src/main/java/org/mineacademy/winter/psycho/PsychoMob1_16.java`
- Psycho 1.12: `src/main/java/org/mineacademy/winter/psycho/PsychoMob1_12.java`
- Psycho 1.8: `src/main/java/org/mineacademy/winter/psycho/PsychoMob1_8.java`
- NMS utilities: `src/main/java/org/mineacademy/winter/psycho/NMSUtil1_12.java`, `NMSUtil1_8.java`
- Permissions: `src/main/java/org/mineacademy/winter/model/Permissions.java`
- Plugin bootstrap: `src/main/java/org/mineacademy/winter/WinterPlugin.java`
