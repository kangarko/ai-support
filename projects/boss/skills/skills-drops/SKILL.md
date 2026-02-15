---
name: boss-skills-drops
description: 'Boss skills (17 abilities) and drop configuration'
---

# Skills and Drops

## Overview

Skills are special abilities that Bosses periodically execute against nearby players. There are 17 built-in skills registered in `BossPlugin.onPluginLoad()`. Each skill has a configurable delay, messages, commands, and type-specific settings. Skills are stored per-Boss inside the `Skills` section of the Boss YAML. Drops control what items appear when a Boss dies, supporting vanilla drops, general floor drops, per-player ranked drops, player commands, and a time threshold for damage tracking.

## Architecture

### Key Classes (Skills)

- `BossSkill` (skill/BossSkill.java): Abstract base class implementing `ConfigSerializable`.
- `AbstractTargetSkill` (skill/AbstractTargetSkill.java): Extends `BossSkill`.
- `TaskBehavior` (task/TaskBehavior.java): The main tick task.

### 17 Built-in Skills

All skills are registered in `BossPlugin.onPluginLoad()`:

1. **Arrow** (`SkillArrow`): Extends `AbstractTargetSkill`. Shoots an arrow at the target player with configurable potion effects on hit. Settings: `Potions` (list of PotionEffect). Default delay: 2-5 seconds. Requires MC 1.11+ (ProjectileHitEvent.getHitEntity).

2. **Bomb** (`SkillBomb`): Extends `AbstractTargetSkill`. Launches a primed TNT toward the target. Settings: `Fuse_Ticks` (int, default 60), `Power` (float, explosion strength). Default delay: 10-25 seconds.

3. **Confuse** (`SkillConfuse`): Extends `AbstractTargetSkill`. Applies Nausea (CONFUSION) and Blindness potion effects to the target. Settings: `Duration` (ticks). Default delay: 15-30 seconds.

4. **Disarm** (`SkillDisarm`): Extends `AbstractTargetSkill`. Drops the target player's held item on the ground. No custom settings. Default delay: 20-40 seconds.

5. **Enderman** (`SkillEnderman`): Extends `AbstractTargetSkill`. Teleports the Boss directly behind the target player (like an Enderman). No custom settings. Default delay: 5-10 seconds.

6. **Ignite** (`SkillIgnite`): Extends `AbstractTargetSkill`. Sets the target player on fire. Settings: `Duration` (ticks). Default delay: 10-20 seconds.

7. **Fireball** (`SkillFireball`): Extends `AbstractTargetSkill`. Launches a fireball toward the target. Settings: `Yield` (float, explosion power), `Incendiary` (boolean, sets fires). Default delay: 5-15 seconds.

8. **Freeze** (`SkillFreeze`): Extends `AbstractTargetSkill`. Freezes the target player in place for a duration. Uses `TaskFrozenPlayers` to manage frozen state. Settings: `Duration` (ticks). Default delay: 15-30 seconds.

9. **Lightning** (`SkillLightning`): Extends `AbstractTargetSkill`. Strikes lightning at the target player's location. Settings: `Damage` (boolean, whether lightning deals damage). Default delay: 10-20 seconds.

10. **Minions** (`SkillMinions`): Extends `AbstractTargetSkill`. Spawns other Bosses as reinforcements near the target. Settings: `Boss_Names` (set of Boss names to spawn), `Radius` (int, 1-50, spawn radius), `Amount` (int, 1-20, how many per Boss). Spawned minions target the player. Default delay: 30 seconds - 1 minute.

11. **Potions** (`SkillPotion`): Extends `AbstractTargetSkill`. Applies configurable potion effects to the target. Settings: `Potions` (list of PotionEffect). Default delay: 10-20 seconds.

12. **StealLife** (`SkillStealLife`): Extends `AbstractTargetSkill`. Steals health from the target and heals the Boss. Settings: `Amount` (double, hearts to steal). Default delay: 10-20 seconds.

13. **Teleport** (`SkillTeleport`): Extends `AbstractTargetSkill`. Teleports the target player to a random location near the Boss. Settings: `Radius` (int, teleport radius). Default delay: 15-30 seconds.

14. **Throw** (`SkillThrow`): Extends `AbstractTargetSkill`. Throws the target player into the air. Settings: `Power` (double, launch velocity). Default delay: 10-20 seconds.

15. **Commands** (`SkillCommands`): Extends `BossSkill` (not target-based). Runs console commands when the skill fires. Does not require a target player. The commands are in the skill's Commands list. Default delay: 10-20 seconds.

16. **Commands_Nearby** (`SkillCommandsNearby`): Extends `BossSkill`. Runs commands for all players within a radius. Settings: `Radius` (int). Default delay: 10-20 seconds.

17. **Commands_Target** (`SkillCommandsTarget`): Extends `AbstractTargetSkill`. Runs commands for the targeted player specifically. Default delay: 10-20 seconds.

### Skill Configuration in Boss YAML

Skills are stored under the `Skills` key in each Boss file:

```yaml
Skills:
  Arrow:
    Delay: "3 seconds - 7 seconds"
    Commands:
      - Type: SKILL
        Command: "tell &eYou've been shot!"
        Console: true
        Chance: 1.0
    Messages:
      - "&c{boss_alias} &7shoots an arrow at you!"
    Stop_More_Skills: true
    Settings:
      Potions:
        - effect: POISON
          duration: 100
          amplifier: 1
  Minions:
    Delay: "30 seconds - 1 minute"
    Commands: []
    Messages:
      - "&c{boss_alias} &7summons minions!"
    Stop_More_Skills: true
    Settings:
      Boss_Names: [MinionZombie]
      Radius: 5
      Amount: 3
```

### Skill Properties

- **Delay**: `RangedSimpleTime` format like `3 seconds - 7 seconds`. A random value within the range is picked for each execution cycle. This is the cooldown between skill activations.
- **Commands**: List of `BossCommand` objects with type SKILL. Executed when the skill fires successfully. Support all special command prefixes (broadcast, tell, discord, etc.) and variables.
- **Messages**: List of strings. One is picked randomly and sent to the target player when the skill fires. Supports `&` color codes and Boss variables.
- **Stop_More_Skills**: If true (default), when this skill fires successfully, no further skills are checked for this Boss in the same tick. Set to false to allow multiple skills per tick.
- **Settings**: Skill-specific configuration map. Varies by skill type (see each skill description above).

## Common Issues & Solutions

- **Skills not firing**: Enable `Debug: [skills]` in settings.yml. Check that the skill delay has elapsed, the Boss has a valid target (for target-based skills), and the target is within `Settings.Skills.TARGET_RANGE` (default 8 blocks). Skills only fire when the Boss is alive in a loaded chunk.
- **Arrow skill not available**: Requires MC 1.11+ due to `ProjectileHitEvent.getHitEntity()`. On older versions, it returns `isCompatible() = false` and is not shown.
- **Minions not spawning**: Ensure the Boss names in `Boss_Names` match existing Boss file names exactly. Check that the minion Boss's limits are not exceeded. The minions target the player after spawning.
- **Skill commands containing {player} not running**: Target-based skills pass the target player. However, the `Commands` skill (non-target) does not have a player context, so `{player}` and `{killer}` will cause the command to be skipped. Use `Commands_Target` or `Commands_Nearby` instead.
- **Player drops not working**: Verify the player dealt damage within the `Player_Time_Threshold` window. Check the damage cache by enabling `Debug: [commands]`. If the Boss died to environment or another mob (no player killer), the system uses the damage cache to find top damagers.
- **General drops all appearing**: Each item rolls its chance independently. A 1.0 chance means the item always drops. Reduce chances if too many items are dropping.
- **Stop_More_Skills confusion**: Default is true. If you want multiple skills to fire in the same tick, set `Stop_More_Skills: false` on earlier skills in the list. Skills are checked in registration order.
- **Freeze skill players stuck**: The `TaskFrozenPlayers` task manages frozen state. If the plugin is reloaded while players are frozen, `onPluginStop()` calls `unfreezeAll()`. If a player logs out while frozen, they are unfrozen on next login.

## Key File Paths

- `src/main/java/org/mineacademy/boss/skill/BossSkill.java` - Base skill class with registration, serialization, delay, commands, messages
- `src/main/java/org/mineacademy/boss/skill/AbstractTargetSkill.java` - Target-based skill base class
- `src/main/java/org/mineacademy/boss/skill/SkillArrow.java` - Arrow skill (potion arrows)
- `src/main/java/org/mineacademy/boss/skill/SkillBomb.java` - Bomb/TNT skill
- `src/main/java/org/mineacademy/boss/skill/SkillConfuse.java` - Nausea + Blindness skill
- `src/main/java/org/mineacademy/boss/skill/SkillDisarm.java` - Drop held item skill
- `src/main/java/org/mineacademy/boss/skill/SkillEnderman.java` - Teleport-behind skill
- `src/main/java/org/mineacademy/boss/skill/SkillIgnite.java` - Fire skill

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
