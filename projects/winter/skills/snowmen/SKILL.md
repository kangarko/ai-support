---
name: snowmen
description: 'Snowman protection, damage, Psycho hostile snowmen, and mob-to-snowman transformation'
---

# Snowman Features

## Overview

Winter enhances Minecraft snowmen with four systems: melt damage prevention, monster targeting prevention, snowball damage dealing, and mob-to-snowman transformation. An experimental Psycho system replaces normal snowmen with hostile NMS-level custom entities that actively attack players using melee and ranged attacks with custom sounds.

## Architecture

### Key Classes

- `SnowmanDamageListener` -- Cancels `EntityDamageEvent` with `DamageCause.MELTING` for snowmen when `Snowman.Enabled` and `Snowman.Disable_Melt_Damage` are both true.
- `SnowmanTargetListener` -- Cancels `EntityTargetLivingEntityEvent` when the target is a snowman and `Snowman.Prevent_Target` is true.
- `SnowmanDealDamageListener` -- Two-part listener.
- `SnowmanTransformListener` -- On `CreatureSpawnEvent`: if the spawning entity type is in `Snowman.Transform.Applicable` and a random roll succeeds (`Chance_Percent`), cancels the spawn and spawns a vanilla snowman instead.
- `PsychoMob` -- Listener and factory for hostile snowmen.
- `PsychoMobModern` -- NMS snowman for MC 1.20.5+.
- `PsychoMob1_16` -- NMS snowman for MC 1.16.x.
- `PsychoMob1_12` -- NMS snowman for MC 1.12.x.
- `PsychoMob1_8` -- NMS snowman for MC 1.8.8.

### Version Compatibility

Psycho mob is compatible with: MC 1.8.8, 1.12, 1.16, 1.20.5+. The `IS_COMPATIBLE` static flag is computed at class load time. Cauldron servers are explicitly excluded. When `Convert_New` or `Convert_Existing` is enabled on an incompatible version, a warning is logged: "Psycho is not compatible with your MC version."

### Registration (WinterPlugin.onPluginStart)

All snowman listeners are conditionally registered based on settings:

- `PsychoMob` listener: registered if `PsychoMob.IS_COMPATIBLE` is true (regardless of Psycho settings, since `Convert_New`/`Convert_Existing` can be changed at runtime).
- `SnowmanDamageListener`: registered if `Snowman.Enabled` AND `Snowman.Disable_Melt_Damage` are true.
- `SnowmanDealDamageListener`: registered if `Snowman.Enabled` AND `Snowman.Damage.Snowball > 0`.
- `SnowmanTargetListener`: registered if `Snowman.Enabled` AND `Snowman.Prevent_Target` are true.
- `SnowmanTransformListener`: registered if `Snowman.Enabled` AND `Snowman.Transform.Enabled` are true.

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

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
