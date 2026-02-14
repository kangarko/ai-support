---
name: boss-skills-drops
description: 'Boss skills (17 abilities) and drop configuration'
---

# Skills and Drops

## Overview

Skills are special abilities that Bosses periodically execute against nearby players. There are 17 built-in skills registered in `BossPlugin.onPluginLoad()`. Each skill has a configurable delay, messages, commands, and type-specific settings. Skills are stored per-Boss inside the `Skills` section of the Boss YAML. Drops control what items appear when a Boss dies, supporting vanilla drops, general floor drops, per-player ranked drops, player commands, and a time threshold for damage tracking.

## Architecture

### Key Classes (Skills)

- `BossSkill` (skill/BossSkill.java): Abstract base class implementing `ConfigSerializable`. Holds: name, boss reference, delay (RangedSimpleTime), commands (List of BossCommand with type SKILL), messages (List of String, one picked randomly), stopMoreSkills (boolean). Abstract methods: `execute(LivingEntity boss)`, `getIcon()`, `getDefaultDelay()`, `getDefaultMessage()`. Optional overrides: `isCompatible()`, `canApplyTo(Boss)`, `getMenu(Menu)`, `readSettings(SerializedMap)`, `writeSettings()`. Skills are registered via `BossSkill.registerSkill(name, class)` and instantiated via `BossSkill.createInstance()`.
- `AbstractTargetSkill` (skill/AbstractTargetSkill.java): Extends `BossSkill`. Wraps `execute()` to find the Boss's current target player using `EntityUtil.getTarget()`. Checks target is a Player, in the same world, within `Settings.Skills.TARGET_RANGE` blocks (default 8), and targetable. If the target skill succeeds, it also calls `executeSkillCommands()`.
- `TaskBehavior` (task/TaskBehavior.java): The main tick task. Every second, iterates all alive Bosses, checks each Boss's skills. For each skill, checks if the randomized delay has elapsed, then calls `skill.execute()`. If `stopMoreSkills` is true on a skill and it succeeds, no further skills are checked for that Boss in that tick.

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

## Drops Configuration

Drops are configured in the `Drops` section of each Boss YAML.

### Drop Types

#### Vanilla Drops
```yaml
Drops:
  Vanilla: true
```
If true, the Boss also drops whatever the vanilla entity type would normally drop. Set to false to disable vanilla drops entirely.

#### General Drops
```yaml
Drops:
  General:
    - Key: diamond_sword{Enchantments:[{id:sharpness,lvl:5}]}
      Value: 0.5
    - Key: diamond
      Value: 1.0
    - Key: golden_apple
      Value: 0.25
```
A list of Tuple(ItemStack, Double). The ItemStack is the item, and the Double is the drop chance (0.0-1.0). These items are dropped on the floor at the Boss's death location for anyone to pick up. Each item rolls independently.

#### Player Drops (Top Damager Rewards)
```yaml
Drops:
  Player:
    - diamond_sword: 1.0
      diamond_helmet: 0.5
    - diamond: 1.0
    - gold_ingot: 1.0
```
A list of maps (ItemStack to Double chance). The list is ordered by damage rank: index 0 = top damager, index 1 = second damager, etc. Items are given directly to the player's inventory (not dropped on floor). Each map entry is an item with its own drop chance. The damage ranking uses a time-filtered cache of all damage dealt to the Boss.

#### Player Time Threshold
```yaml
Drops:
  Player_Time_Threshold: "15 seconds"
```
How far back in time to account for player damage. Default: 15 seconds. Only damage dealt within this window before death counts toward the ranking. This prevents a player who hit the Boss once 10 minutes ago from claiming top rewards.

#### Player Commands
```yaml
Drops:
  Player_Commands:
    - "give {player} diamond 1"
    - "eco give {player} 100"
```
Console commands run for players in the top damager list. Each command runs for each qualifying player in order (top damager first). Support all Boss variables including `{player}`, `{boss_name}`, etc. The `Death.Run_PvP_Commands_As_Console` setting (settings.yml, default true) controls whether these run as console or as the player.

### Dropped Experience
```yaml
Dropped_Exp: "10 - 50"
```
Ranged value for XP orbs dropped on death. Set to `default` or `-1` to use vanilla XP rules.

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
- `src/main/java/org/mineacademy/boss/skill/SkillFireball.java` - Fireball projectile skill
- `src/main/java/org/mineacademy/boss/skill/SkillFreeze.java` - Freeze-in-place skill
- `src/main/java/org/mineacademy/boss/skill/SkillLightning.java` - Lightning strike skill
- `src/main/java/org/mineacademy/boss/skill/SkillMinions.java` - Spawn reinforcement Bosses
- `src/main/java/org/mineacademy/boss/skill/SkillPotion.java` - Apply potion effects skill
- `src/main/java/org/mineacademy/boss/skill/SkillStealLife.java` - Steal health skill
- `src/main/java/org/mineacademy/boss/skill/SkillTeleport.java` - Teleport target skill
- `src/main/java/org/mineacademy/boss/skill/SkillThrow.java` - Launch target into air skill
- `src/main/java/org/mineacademy/boss/skill/SkillCommands.java` - Run console commands skill
- `src/main/java/org/mineacademy/boss/skill/SkillCommandsNearby.java` - Commands for nearby players
- `src/main/java/org/mineacademy/boss/skill/SkillCommandsTarget.java` - Commands for target player
- `src/main/java/org/mineacademy/boss/BossPlugin.java` - Skill registration in onPluginLoad()
- `src/main/java/org/mineacademy/boss/task/TaskBehavior.java` - Skill execution tick loop
- `src/main/java/org/mineacademy/boss/task/TaskFrozenPlayers.java` - Freeze skill state management
- `src/main/java/org/mineacademy/boss/listener/SkillListener.java` - Skill event handlers (arrow hit, etc.)
- `src/main/java/org/mineacademy/boss/model/Boss.java` - Drop loading/saving (loadGeneralDrops, loadPlayerDrops, Drops section)
