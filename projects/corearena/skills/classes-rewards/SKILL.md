---
name: corearena-classes-rewards
description: 'Class system, tier upgrades, experience formulas, nugget economy, and reward mechanics'
---

# CoreArena - Classes, Economy & Rewards

## Overview

CoreArena has a class-based equipment system, an in-arena experience/level system, a persistent nugget currency, and a rewards shop. Players pick a class in the lobby, fight monsters to earn experience during the game, and after the game their earned levels convert to nuggets which they spend on class tier upgrades and material rewards.

## Architecture

### Key Classes

- `SimpleClass` (`impl/SimpleClass.java`) -- Loads class config from `classes/<name>.yml` (generated from `prototype/class.yml`).
- `ClassTier` (`model/ClassTier.java`) -- Interface for a single tier of a class.
- `SimpleTier` (`impl/SimpleTier.java`) -- Implementation of `ClassTier`.
- `TierSettings` (`model/TierSettings.java`) -- Holds per-tier potions and permissions loaded from the class YAML file.
- `SimpleUpgrade` (`impl/SimpleUpgrade.java`) -- Loads upgrade config from `upgrades/<name>.yml` (generated from `prototype/upgrade.yml`).
- `SimpleReward` (`impl/SimpleReward.java`) -- A purchasable reward item with a type (ITEM, BLOCK, PACK), item stack, and nugget cost.
- `ExpFormula` (`exp/ExpFormula.java`) -- Evaluates mathematical expressions with placeholders: `{phase}`, `{reward}`, `{players}`, `{maxPlayers}`.
- `ClassManager` (`manager/ClassManager.java`) -- Registry of all loaded classes.
- `UpgradesManager` (`manager/UpgradesManager.java`) -- Registry of all loaded upgrades.
- `RewardsManager` (`manager/RewardsManager.java`) -- Manages the reward shop items and purchases.

### Data Flow

1. **Class creation**: Admin creates `classes/<name>.yml`. Tier inventories are set via `/arena menu <class>` GUI.
2. **Class selection**: During lobby, player clicks a class sign or uses `/arena class` menu. `SimpleClass.giveToPlayer()` assigns the class, sets tier, gives inventory.
3. **In-arena experience**: Killing mobs drops exp items (`ExpItemHandler.spawn()`). Players pick them up or get exp directly if `Give_To_Killer` is true. Exp accumulates in `InArenaCache`, displayed via XP bar.
4. **Leveling**: When exp exceeds `Exp_Per_Level` (default 30), player levels up. Levels are in-arena only.
5. **Nugget conversion**: When player leaves arena, their in-arena levels are multiplied by `Level_To_Nugget_Conversion_Ratio` (default 0.5) and added to their persistent nugget balance.
6. **Spending nuggets**: Players use `/arena rewards` menu to buy material rewards or upgrade class tiers.

## Common Issues & Solutions

**"Found too low class tier for player"**
The player's tier for the assigned class is below `Required_Class_Tier` in the arena config. Either upgrade the player's tier or lower the arena requirement.

**Player kicked with "no class" on arena start**
The player did not select a class during lobby. If `Give_Random_Class_If_Not_Selected` is false in settings.yml, they are kicked. If true but the player lacks permission for all classes, they are also kicked.

**Experience not dropping**
Check that `Experience.Item` in settings.yml is not set to `none`. If `Give_To_Killer` is true, exp goes directly to the killer's bar instead of dropping an item.

**Nuggets not awarded after leaving**
Check `Experience.Reward_On_Escape`. If false and the player left via command/disconnect, no nuggets are given. Also, the arena must have been in RUNNING state (not LOBBY).

**Upgrade sign says "locked"**
The current arena phase is below the upgrade's `Available_From_Phase`. Players must wait for the correct phase.

**Potions not applied**
Verify the format in the class YAML: `POTION_TYPE LEVEL: DURATION`. The potion name must match a valid Bukkit `PotionEffectType`. Level is 1-based (level 1 = amplifier 0 internally).

**Class permission not working**
The `Permission` field in class YAML uses `{file_lowercase}` which is replaced with the lowercase filename. So `classes/Warrior.yml` requires `corearena.class.warrior`.

## Key File Paths

| File | Purpose |
|------|---------|
| `src/main/java/org/mineacademy/corearena/impl/SimpleClass.java` | Class loading, tier resolution, giving to player |
| `src/main/java/org/mineacademy/corearena/impl/SimpleTier.java` | Tier inventory storage |
| `src/main/java/org/mineacademy/corearena/model/TierSettings.java` | Per-tier potions and permissions |
| `src/main/java/org/mineacademy/corearena/impl/SimpleUpgrade.java` | Upgrade loading and item giving |
| `src/main/java/org/mineacademy/corearena/impl/SimpleReward.java` | Reward item with cost |
| `src/main/java/org/mineacademy/corearena/exp/ExpFormula.java` | Math expression evaluator for exp |
| `src/main/java/org/mineacademy/corearena/manager/ClassManager.java` | Class registry |
| `src/main/java/org/mineacademy/corearena/manager/UpgradesManager.java` | Upgrade registry |

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
