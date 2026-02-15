---
name: boss-creation
description: 'Boss creation, configuration, and the Boss model'
---

# Boss Creation and Configuration

## Overview

Bosses are custom Minecraft mobs with configurable health, equipment, attributes, skills, drops, commands, and visual effects. Each Boss is stored as a YAML file in the `bosses/` folder and loaded via the `ConfigItems` system. Bosses are created with `/boss new <entityType>`, which opens a chat prompt for the Boss name, then generates the YAML file.

## Architecture

### Key Classes

- `Boss` (model/Boss.java): The main model class extending `YamlConfig`.
- `BossAttribute` (model/BossAttribute.java): Enum of 24 attributes that can be applied to a Boss entity.
- `CustomSetting` (custom/CustomSetting.java): Abstract class for entity-type-specific settings stored under `Custom_Settings` in the Boss YAML.
- `BossReinforcement` (model/BossReinforcement.java): Configures entities or other Bosses that spawn when the Boss dies.
- `BossCitizensSettings` (model/BossCitizensSettings.java): Citizens NPC integration settings: Enabled, Speed, Skin, Sound_Death, Sound_Hurt, Sound_Ambient, Goal_Target_Enabled, Goal_Target_Aggressive, Goal_Target_Radius, Goal_Target_Entities,...
- `SpawnedBoss` (model/SpawnedBoss.java): Represents a live Boss in the world.
- `BossPlugin` (BossPlugin.java): Main plugin class.

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

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
