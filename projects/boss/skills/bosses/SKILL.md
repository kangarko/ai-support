---
name: boss-creation
description: 'Boss creation, configuration, and the Boss model'
---

# Boss Creation and Configuration

## Overview

Bosses are custom Minecraft mobs with configurable health, equipment, attributes, skills, drops, commands, and visual effects. Each Boss is stored as a YAML file in the `bosses/` folder and loaded via the `ConfigItems` system. Bosses are created with `/boss new <entityType>`, which opens a chat prompt for the Boss name, then generates the YAML file.

## Architecture

### Key Classes

- `Boss` (model/Boss.java): The main model class extending `YamlConfig`. Holds all Boss properties (type, alias, health, equipment, attributes, skills, drops, commands, riding, reinforcements, limits, citizens settings, custom settings, egg config). Handles spawning logic, property application, variable replacement, command execution, and damage tracking.
- `BossAttribute` (model/BossAttribute.java): Enum of 24 attributes that can be applied to a Boss entity. Each maps to a Bukkit `CompAttribute` (except DAMAGE_MULTIPLIER which is custom). Includes: ARMOR, ARMOR_TOUGHNESS, ATTACK_DAMAGE, ATTACK_KNOCKBACK, ATTACK_SPEED, BURNING_TIME, EXPLOSION_KNOCKBACK_RESISTANCE, FALL_DAMAGE_MULTIPLIER, FLYING_SPEED, FOLLOW_RANGE, GRAVITY, JUMP_STRENGTH, KNOCKBACK_RESISTANCE, LUCK, MAX_ABSORPTION, MOVEMENT_EFFICIENCY, MOVEMENT_SPEED, OXYGEN_BONUS, SAFE_FALL_DISTANCE, SCALE, STEP_HEIGHT, TEMPT_RANGE, WATER_MOVEMENT_EFFICIENCY, ZOMBIE_SPAWN_REINFORCEMENTS, and DAMAGE_MULTIPLIER.
- `CustomSetting` (custom/CustomSetting.java): Abstract class for entity-type-specific settings stored under `Custom_Settings` in the Boss YAML. Preinstalled settings: Baby, Creeper_Powered, Despawn, Enderdragon_Grief, Enderman_Teleport, Gravity, Invulnerable, Iron_Golem_Aggressive, NoAI, Pickup_Items, Silent, Slime_Babies_On_Death, Snowman_Pumpkin, Sun_Damage, Targetable, Zombie_Villager, Phantom_Size, Slime_Size, Ender_Dragon_Phase, Rabbit_Type, Skeleton_Type, Villager_Profession, Villager_Type, Glowing, Custom_Name_Visible.
- `BossReinforcement` (model/BossReinforcement.java): Configures entities or other Bosses that spawn when the Boss dies. Has Boss_Name or Entity_Type, Amount, and Chance fields.
- `BossCitizensSettings` (model/BossCitizensSettings.java): Citizens NPC integration settings: Enabled, Speed, Skin, Sound_Death, Sound_Hurt, Sound_Ambient, Goal_Target_Enabled, Goal_Target_Aggressive, Goal_Target_Radius, Goal_Target_Entities, Goal_Wander_Enabled, Goal_Wander_Radius.
- `SpawnedBoss` (model/SpawnedBoss.java): Represents a live Boss in the world. Links the Boss config to the living entity.
- `BossPlugin` (BossPlugin.java): Main plugin class. Registers skills, hooks, listeners, tasks, variables, and loads data.

### Boss YAML Structure

Each Boss file (`bosses/<name>.yml`) contains:

```yaml
Type: ZOMBIE
Alias: "&cZombie Boss"
Health: 100.0
Dropped_Exp: "10 - 50"
Equipment:
  HAND:
    Key: diamond_sword
    Value: 0.5
  HELMET:
    Key: diamond_helmet
    Value: 0.1
Random_Equipment_On_Empty_Slots: false
Potion_Effects:
  SPEED: 2
  STRENGTH: 1
Riding:
  Vanilla: [SPIDER]
  Boss: [AnotherBossName]
  Remove_On_Death: false
Commands:
  - Type: SPAWN
    Command: "broadcast &eBoss {boss_name} spawned!"
    Console: true
    Chance: 1.0
  - Type: DEATH
    Command: "tell &cYou killed {boss_name}!"
    Console: true
    Chance: 1.0
  - Type: HEALTH_TRIGGER
    Command: "broadcast &eBoss is below 50%!"
    Console: true
    Chance: 1.0
    Health_Trigger: 50.0
Commands_Stop_After_First: false
Attributes:
  MOVEMENT_SPEED: 0.35
  ATTACK_DAMAGE: 15.0
  FOLLOW_RANGE: 40.0
  SCALE: 2.0
  DAMAGE_MULTIPLIER: 1.5
Lightning:
  Death: true
  Spawn: true
Reinforcements:
  - Boss_Name: MinionBoss
    Amount: 3
    Chance: 0.5
  - Entity_Type: ZOMBIE
    Amount: 5
    Chance: 1.0
Custom_Settings:
  Baby: false
  Despawn: false
  NoAI: false
  Glowing: true
Skills: {}
Drops:
  Vanilla: true
  General:
    - Key: diamond
      Value: 0.5
  Player:
    - diamond_sword: 1.0
  Player_Time_Threshold: "15 seconds"
  Player_Commands:
    - "give {player} diamond 1"
Limit_Reasons: [SPAWN_RULE]
Limit:
  Nearby_Bosses:
    Key: 100
    Value: 20.0
  Worlds:
    world: 5
Citizens:
  Enabled: false
  Speed: 1.0
  Skin: Notch
  Sound_Death: entity.wither.death
  Sound_Hurt: entity.wither.hurt
  Sound_Ambient: entity.wither.ambient
  Goal_Target_Enabled: true
  Goal_Target_Aggressive: true
  Goal_Target_Radius: 24
  Goal_Target_Entities: [PLAYER]
  Goal_Wander_Enabled: true
  Goal_Wander_Radius: 18
Keep_In_Spawn_Region: false
Egg:
  Material: ZOMBIE_SPAWN_EGG
  Title: "&cZombie Boss Egg"
  Lore:
    - "&7Right-click to spawn"
Native_Attack_Goal_Enabled: false
Use_Custom_Model: false
Custom_Models: []
Use_Custom_Attack_Animation: false
Custom_Attack_Animations: []
```

## Configuration

### Creating a Boss

1. Run `/boss new <entityType>` (e.g., `/boss new zombie`).
2. A chat prompt asks for the Boss name. Type the name and press Enter.
3. The Boss YAML file is created in `bosses/<name>.yml`.
4. Use `/boss menu <name>` to open the GUI editor, or edit the YAML directly.

### Entity Type

The `Type` key is required. It must be a valid Bukkit EntityType. Use `/boss new` tab completion to see valid types. The Boss type is set at creation and typically should not be changed afterward.

### Alias

The `Alias` is the display name shown above the Boss entity and used in `{boss_alias}` variables. Supports `&` color codes and hex colors with `<#RRGGBB>`. Set to `hidden` to completely remove the name tag. Defaults to the Boss file name.

### Health

Set via the `Health` key. If not set, defaults to the entity type's vanilla health. Max health is limited by `spigot.yml > settings.attribute.maxHealth.max`. If the configured health exceeds this, the plugin logs a warning.

### Dropped Experience

`Dropped_Exp` accepts a ranged value like `10 - 50` or a fixed number. Set to `default` or `-1` to use vanilla XP rules.

### Equipment

Configured under `Equipment` with slot keys: HAND, OFF_HAND, HELMET, CHEST, LEGS, FEET. Each slot has a Key (the ItemStack) and Value (drop chance from 0.0 to 1.0). The `Random_Equipment_On_Empty_Slots` boolean controls whether vanilla randomly equips slots that are not configured.

### Attributes

All 24 `BossAttribute` values can be set under `Attributes`. Key values such as MOVEMENT_SPEED (default ~0.23 for zombies), ATTACK_DAMAGE, FOLLOW_RANGE, KNOCKBACK_RESISTANCE (0.0-1.0), and SCALE (1.0 = normal). DAMAGE_MULTIPLIER is a custom attribute (not a Bukkit attribute) that multiplies all damage the Boss deals (0.5 = half, 2.0 = double). ZOMBIE_SPAWN_REINFORCEMENTS only applies to Zombie entity type. Attributes that don't exist for an entity type are silently skipped.

### Riding

Under `Riding`, configure `Vanilla` (list of EntityType) and `Boss` (list of Boss names) for stacking entities. The Boss sits on top of the riding entities. `Remove_On_Death` controls whether riding entities are removed when the Boss dies. Horses are auto-tamed to prevent kicking.

### Potion Effects

`Potion_Effects` is a map of PotionEffectType to amplifier level (1-based). Effects are applied with infinite duration at spawn.

### Commands

The `Commands` list holds `BossCommand` objects with Type (SPAWN, DEATH, HEALTH_TRIGGER, SKILL), Command string, Console boolean, Chance (0.0-1.0), and optional Health_Trigger for HEALTH_TRIGGER type. SKILL type commands are stored per-skill, not in the main Commands list. Special command prefixes: `broadcast`, `tell`, `tell-damagers`, `tell-damagers-list`, `broadcast-damagers-list`, `discord`. Variables available: `{player}`, `{killer}`, `{boss_name}`, `{boss_alias}`, `{boss_location}`, `{boss_world}`, `{boss_x}`, `{boss_y}`, `{boss_z}`, `{damager}`, `{damage}`, `{damage_percent}`, `{damage_percent_N}` (top N), `{order}`. `Commands_Stop_After_First` stops after the first command with a passing chance.

### Lightning

`Lightning.Death` and `Lightning.Spawn` toggle cosmetic lightning strikes.

### Reinforcements

List of `BossReinforcement` objects. Each has either `Boss_Name` (spawn another Boss) or `Entity_Type` (spawn vanilla mob), plus `Amount` and `Chance`.

### Custom Settings

Stored under `Custom_Settings`. These are entity-type-specific toggles. Each setting only shows in the menu if it applies to the Boss's entity type. Examples: Baby (zombies/ageables), NoAI, Despawn, Invulnerable, Silent, Glowing, Slime_Size, Phantom_Size, Villager_Profession, Ender_Dragon_Phase, Enderman_Teleport.

### Citizens NPC

If Citizens plugin is installed, enable `Citizens.Enabled` to spawn the Boss as an NPC. The `PLAYER` entity type always forces Citizens. Settings include custom Skin (player name or URL), custom sounds (Sound_Death, Sound_Hurt, Sound_Ambient), Speed, and pathfinder goals (Goal_Target_Enabled with Aggressive/Radius/Entities, Goal_Wander_Enabled with Radius).

### ModelEngine

If ModelEngine plugin is installed, `Use_Custom_Model: true` and list model IDs in `Custom_Models`. A random model is selected at spawn. Similarly `Use_Custom_Attack_Animation` and `Custom_Attack_Animations` for attack animations.

### Spawning Limits

- `Limit_Reasons`: Which spawn reasons check limits. Default: `[SPAWN_RULE]`. Options from `BossSpawnReason`: COMMAND, SPAWN_RULE, RIDING, REINFORCEMENTS, EGG, API.
- `Limit.Nearby_Bosses`: Key = max bosses, Value = radius in blocks. Prevents spawning when too many of the same Boss exist nearby.
- `Limit.Worlds`: Map of world name to max count of this Boss in that world.

### Keep In Region

`Keep_In_Spawn_Region: true` restricts the Boss to the region it spawned in. `Return_Location_On_Escape_Spawn` sets the exact return point.

### Spawn Egg

`Egg.Material` overrides the spawn egg item. `Egg.Title` and `Egg.Lore` customize the egg appearance.

### Native Attack Goal

`Native_Attack_Goal_Enabled: true` injects a custom pathfinder goal to make passive mobs aggressive. Requires Paper or compatible server with goal API.

## Common Issues & Solutions

- **Boss spawns with wrong health**: Check `spigot.yml > settings.attribute.maxHealth.max`. The configured health must not exceed this value.
- **Boss does not spawn**: Enable debug mode by setting `Debug: [spawning]` in settings.yml. Check console for messages explaining why the spawn was cancelled (limits, Lands integration, API event cancellation, invalid entity type).
- **Equipment not showing**: Only Monsters, Players, Horses, and Armor Stands can have equipment. For horses, only the CHEST slot is used for horse armor.
- **Attributes have no effect**: Some attributes only apply to certain entity types. The plugin silently skips incompatible attributes. Use the GUI menu to see which attributes are available.
- **Citizens Boss not moving**: Ensure Citizens plugin is installed, `Citizens.Enabled: true`, and target/wander goals are configured. Check that the Boss type supports NPC pathfinding.
- **ModelEngine model not found**: The model ID must exactly match what is registered in ModelEngine. Invalid models are auto-removed from the list with a console warning.
- **Riding entities not appearing**: Riding Boss names must match existing Boss files exactly (case-sensitive). A Boss cannot ride itself (infinite loop protection exists).
- **Custom settings not applying**: Custom settings are entity-type-specific. The `canApplyTo` method checks compatibility. For example, Baby only works on Zombies and Ageable entities.
- **Boss commands not running**: If the command contains `{player}` or `{killer}` and no player is available (e.g., the Boss died to environment), the command is skipped with a warning. Set `Debug: [commands]` to see details.

## Key File Paths

- `src/main/java/org/mineacademy/boss/model/Boss.java` - Main Boss model
- `src/main/java/org/mineacademy/boss/model/BossAttribute.java` - Attribute enum (24 attributes)
- `src/main/java/org/mineacademy/boss/model/BossCommand.java` - Command model (Type, Command, Console, Chance, Health_Trigger)
- `src/main/java/org/mineacademy/boss/model/BossCommandType.java` - Command type enum (SPAWN, DEATH, HEALTH_TRIGGER, SKILL)
- `src/main/java/org/mineacademy/boss/model/BossReinforcement.java` - Reinforcement model
- `src/main/java/org/mineacademy/boss/model/BossCitizensSettings.java` - Citizens NPC settings
- `src/main/java/org/mineacademy/boss/model/SpawnedBoss.java` - Live spawned Boss wrapper
- `src/main/java/org/mineacademy/boss/custom/CustomSetting.java` - Custom settings framework (25 built-in settings)
- `src/main/java/org/mineacademy/boss/hook/ModelEngineHook.java` - ModelEngine integration
- `src/main/java/org/mineacademy/boss/hook/CitizensHook.java` - Citizens integration
- `src/main/java/org/mineacademy/boss/model/Permissions.java` - Permission definitions
- `src/main/java/org/mineacademy/boss/settings/Settings.java` - Global settings
- `src/main/resources/settings.yml` - Default settings file
