---
name: corearena-classes-rewards
description: 'Class system, tier upgrades, experience formulas, nugget economy, and reward mechanics'
---

# CoreArena - Classes, Economy & Rewards

## Overview

CoreArena has a class-based equipment system, an in-arena experience/level system, a persistent nugget currency, and a rewards shop. Players pick a class in the lobby, fight monsters to earn experience during the game, and after the game their earned levels convert to nuggets which they spend on class tier upgrades and material rewards.

## Architecture

### Key Classes

- `SimpleClass` (`impl/SimpleClass.java`) -- Loads class config from `classes/<name>.yml` (generated from `prototype/class.yml`). Manages permission checks, tier lookups, and giving items/potions to players.
- `ClassTier` (`model/ClassTier.java`) -- Interface for a single tier of a class. Each tier holds inventory contents, armor, and potion effects.
- `SimpleTier` (`impl/SimpleTier.java`) -- Implementation of `ClassTier`. Stores items and armor per tier level. Saved in `data.yml`.
- `TierSettings` (`model/TierSettings.java`) -- Holds per-tier potions and permissions loaded from the class YAML file.
- `SimpleUpgrade` (`impl/SimpleUpgrade.java`) -- Loads upgrade config from `upgrades/<name>.yml` (generated from `prototype/upgrade.yml`). Has items to give and an `Available_From_Phase` lock.
- `SimpleReward` (`impl/SimpleReward.java`) -- A purchasable reward item with a type (ITEM, BLOCK, PACK), item stack, and nugget cost.
- `ExpFormula` (`exp/ExpFormula.java`) -- Evaluates mathematical expressions with placeholders: `{phase}`, `{reward}`, `{players}`, `{maxPlayers}`. Used for experience calculation.
- `ClassManager` (`manager/ClassManager.java`) -- Registry of all loaded classes. Provides `findClass()`, `findRandomClassFor()`, `getClassNames()`.
- `UpgradesManager` (`manager/UpgradesManager.java`) -- Registry of all loaded upgrades. Provides `findUpgrade()`, `getAvailable()`.
- `RewardsManager` (`manager/RewardsManager.java`) -- Manages the reward shop items and purchases.

### Data Flow

1. **Class creation**: Admin creates `classes/<name>.yml`. Tier inventories are set via `/arena menu <class>` GUI.
2. **Class selection**: During lobby, player clicks a class sign or uses `/arena class` menu. `SimpleClass.giveToPlayer()` assigns the class, sets tier, gives inventory.
3. **In-arena experience**: Killing mobs drops exp items (`ExpItemHandler.spawn()`). Players pick them up or get exp directly if `Give_To_Killer` is true. Exp accumulates in `InArenaCache`, displayed via XP bar.
4. **Leveling**: When exp exceeds `Exp_Per_Level` (default 30), player levels up. Levels are in-arena only.
5. **Nugget conversion**: When player leaves arena, their in-arena levels are multiplied by `Level_To_Nugget_Conversion_Ratio` (default 0.5) and added to their persistent nugget balance.
6. **Spending nuggets**: Players use `/arena rewards` menu to buy material rewards or upgrade class tiers.

## Configuration

### Class File (`classes/<name>.yml`)

Generated from `prototype/class.yml`:

```yaml
Permission: "corearena.class.{file_lowercase}"

Tiers:
  2:
    Potions:
      SPEED 2: 30 seconds
    Permissions:
      - custom.permission
      - another.random.permission
```

| Key | Type | Description |
|-----|------|-------------|
| `Permission` | string | Permission node required to use this class. `{file_lowercase}` is replaced with the lowercase filename. Set to empty or remove to allow all players. |
| `Tiers.<n>.Potions` | map | Potion effects for this tier. Format: `<POTION_TYPE> <level>: <duration>`. Duration is a time string like `30 seconds`. |
| `Tiers.<n>.Permissions` | list | Permissions granted to the player while they have this tier active in-arena. |

Tier inventory contents (items, armor) are not stored in YAML -- they are set through the in-game GUI (`/arena menu <classname>`) and stored in `data.yml`.

The potion pattern is parsed by regex: `([a-zA-Z_]+)(| ([0-9]{1,2}))$`. Valid potion names come from Bukkit's `PotionEffectType`.

### Upgrade File (`upgrades/<name>.yml`)

Generated from `prototype/upgrade.yml`:

```yaml
Permission: "corearena.class.{file_lowercase}"
Available_From_Phase: 1
```

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `Permission` | string | corearena.class.{file_lowercase} | Permission required to access this upgrade. |
| `Available_From_Phase` | int | 1 | The arena phase from which this upgrade becomes purchasable. |

Upgrade items are configured via `/arena menu <upgradename>` GUI and stored in `data.yml`.

### Experience Settings (`settings.yml` -> `Experience` section)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `Experience.Give_To_Killer` | boolean | false | Give exp directly to killer instead of dropping item. |
| `Experience.Exp_Per_Level` | double | 30 | Experience points needed per level. |
| `Experience.Level_To_Nugget_Conversion_Ratio` | double | 0.5 | Multiplier: levels * ratio = nuggets earned. E.g. 20 levels * 0.5 = 10 nuggets. |
| `Experience.Reward_On_Escape` | boolean | true | Give nuggets to players who leave via command/disconnect/sign. |
| `Experience.Item` | material | LIGHT_BLUE_DYE | Material for dropped experience items. Set to `none` to disable drops. |
| `Experience.Item_Label` | string | `&b{amount} exp` | Display name of experience items. `{amount}` is replaced with exp value. |

### Experience Formulas (`settings.yml` -> `Experience.Amount`)

Formulas are mathematical expressions evaluated at runtime. Available placeholders:

- `{phase}` -- Current arena phase number.
- `{reward}` -- Reward value (used in reward calculations).
- `{players}` -- Current player count in arena.
- `{maxPlayers}` -- Maximum players configured for arena.

| Key | Default Formula | Description |
|-----|----------------|-------------|
| `Experience.Amount.Next_Phase` | `"5 + (5 * {phase})"` | Exp awarded to all players when a new phase starts. |
| `Experience.Amount.Kill.Global` | `"10 + (5 * {phase})"` | Default exp for killing any mob not listed specifically. |
| `Experience.Amount.Kill.Player` | `"30 + (6 * {phase})"` | Exp for killing a player (when PvP is enabled). |
| `Experience.Amount.Kill.<ENTITY_TYPE>` | varies | Exp for killing a specific entity. Key must match Bukkit EntityType name (case-sensitive) or a Boss/MythicMobs name. |

Per-arena overrides: Each arena file can define its own `Experience` section that overrides these global formulas.

### Gold Item

The Gold item converts nuggets to economy money (requires Vault).

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `Experience.Gold.Conversion_Ratio` | int | 100 | How much 1 piece of Gold is worth in economy currency. |
| `Experience.Gold.Currency_Backup_Name` | string | `$` | Fallback currency name if Vault returns empty. |

Obtained via `/arena items` menu.

### Rewards Settings (`settings.yml` -> `Rewards` section)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `Rewards.Allow_Skipping_Tier` | boolean | false | Allow upgrading from tier 1 directly to tier 4, skipping 2 and 3. |
| `Rewards.Enable_Material_Rewards` | boolean | true | Show Items/Blocks/Packs buttons in rewards menu. If false, menu jumps to class upgrade menu. |
| `Rewards.Menu_Items.Items` | material | EMERALD | Material for the Items tab in rewards menu. |
| `Rewards.Menu_Items.Blocks` | material | OAK_LOG | Material for the Blocks tab. |
| `Rewards.Menu_Items.Packs` | material | WITHER_SKELETON_SKULL | Material for the Packs tab. |

### Per-Arena Wave Rewards (in arena YAML)

```yaml
Rewards:
  Every:
    5:
    - "iron_ingot:16"
    - "gold_ingot:8"
    - "diamond:1"
  At:
    10:
    - "iron_sword"
    - "iron_pickaxe"
    20:
    - "/cc give physical dungeons 1 {player}"
    30:
    - "golden_apple:1:warrior"
```

- `Every.<n>` -- Give these rewards every nth wave.
- `At.<n>` -- Give these rewards exactly at wave n.
- Item format: `material_name` or `material_name:amount` or `material_name:amount:required_class`.
- Command format: Start with `/`. Use `{player}` placeholder.

## Class Lifecycle

1. **Admin creates class**: Place file in `classes/` or use the menu system.
2. **Admin sets tier inventory**: `/arena menu <classname>` opens GUI. Place items in inventory slots, save.
3. **Player selects class**: In lobby, click a `[class]` sign or use `/arena class` menu. The class is "previewed" (given with `TierMode.PREVIEW`).
4. **Arena starts**: If player has no class and `Give_Random_Class_If_Not_Selected` is true, a random permitted class is assigned. Otherwise player is kicked. The class is given with `TierMode.PLAY`.
5. **Player respawns**: Class inventory is re-given after 10 ticks delay.
6. **Player leaves**: Tier's `onArenaLeave()` is called (removes granted permissions/effects). Original inventory restored.

### Tier Resolution

When giving a class to a player, `SimpleClass.getMinimumTier(playerTier)` is called. If the player's exact tier does not exist, it falls back to the highest available tier below the player's level. This means not every tier number needs a defined inventory.

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
| `src/main/java/org/mineacademy/corearena/manager/RewardsManager.java` | Reward shop management |
| `src/main/java/org/mineacademy/corearena/settings/Settings.java` | Global settings (Experience, Rewards sections) |
| `src/main/resources/prototype/class.yml` | Default class config template |
| `src/main/resources/prototype/upgrade.yml` | Default upgrade config template |
| `src/main/resources/settings.yml` | Global settings file |
