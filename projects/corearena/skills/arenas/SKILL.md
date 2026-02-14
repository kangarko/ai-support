---
name: corearena-arenas
description: 'Arena creation, lifecycle states, per-arena config keys, setup tools, and phase system'
---

# CoreArena - Arenas

## Overview

CoreArena is a Minecraft mob-arena plugin. Each arena is a self-contained instance where players fight waves (phases) of monsters. Arenas follow a strict lifecycle: STOPPED -> LOBBY -> RUNNING -> STOPPED. Configuration lives in individual YAML files under `arenas/<name>.yml`, auto-generated from `prototype/arena.yml`.

## Architecture

### Key Classes

- `SimpleArena` (`impl/arena/SimpleArena.java`) -- Abstract base implementing the `Arena` interface. Owns the lifecycle state machine, player join/leave logic, entity cleanup, snapshot restore, and phase/countdown management. All state transitions are `final` methods.
- `FeatureArena` (`impl/arena/FeatureArena.java`) -- Extends `SimpleArena`. Adds lives system, class assignment on arena start, random spawn points, PvP phase gating, block break/place allow-lists, experience drops on entity death, and item interactions (TNT ignition, wolf spawning, fireball launching).
- `MobArena` (`impl/arena/MobArena.java`) -- Concrete arena type extending `FeatureArena`. The standard "last player standing" mob arena.
- `ArenaState` (`type/ArenaState.java`) -- Enum with three values: `STOPPED`, `LOBBY`, `RUNNING`.
- `NextPhaseMode` (`type/NextPhaseMode.java`) -- Enum: `TIMER` (phase advances on timer) or `MONSTERS` (phase advances when all aggressive mobs are killed).
- `SimpleSettings` (`impl/SimpleSettings.java`) -- Loads and holds all per-arena config from `arenas/<name>.yml`. Implements `ArenaSettings`.
- `SimpleSetup` (`impl/SimpleSetup.java`) -- Tracks setup readiness: requires lobby point, region (primary + secondary), and at least one player spawn point.
- `SimplePhaseIncremental` (`impl/SimplePhaseIncremental.java`) -- Phase timer implementation. Handles chest refill triggers and phase progression.
- `ArenaCommands` (`model/ArenaCommands.java`) -- Holds and executes Player/Player_Console/Console command lists for arena lifecycle hooks. Supports `@tell` and `@connect` prefixes.
- `StopCause` (`type/StopCause.java`) -- Enum of reasons an arena can stop: `NATURAL_COUNTDOWN`, `NATURAL_NO_MONSTERS`, `INTERRUPTED_LAST_PLAYER_LEFT`, `INTERRUPTED_COMMAND`, `INTERRUPTED_ERROR`, `CANCELLED_NOT_ENOUGH_PLAYERS`.
- `LeaveCause` (`type/LeaveCause.java`) -- Enum of reasons a player leaves: `COMMAND`, `KILLED`, `ARENA_END`, `DISCONNECT`, `ESCAPED`, `NO_ENOUGH_CLASS`, `NOT_READY`, `ERROR`.

### Lifecycle Flow

1. **STOPPED**: Arena is idle. No players.
2. **Player joins** (`joinPlayer`): Checks permissions (`corearena.command.join.{arena}`), arena not running/full/edited, player not already in another arena, inventory empty (if `Store_Inventories` is false). Teleports player to lobby.
3. **LOBBY**: First join triggers `startLobby()`. Sets state to `LOBBY`, clears entities, runs `Lobby_Start` commands, starts `LaunchCountdown` (configurable via `Duration.Lobby`).
4. **Countdown expires or `/arena start`**: Calls `startArena()`. Checks minimum player count. Sets state to `RUNNING`, cancels lobby countdown, starts `EndCountdown` (configurable via `Duration.Arena`), starts phase timer, assigns classes and spawn points, runs `Start` commands.
5. **RUNNING**: Phases advance per `Next_Phase_Mode`. Monsters spawn. Players fight. Experience is collected. Rewards given per wave config.
6. **Arena ends**: Triggered by countdown expiry, all monsters killed (if `Arena_End_No_Monsters` is set), max phase reached, last player leaving, or `/arena stop`. Calls `stopArena()`: cancels countdowns, resets phase, removes entities, restores snapshot, runs `Finish` commands (if natural end) then `End` commands, removes all players, sets state back to `STOPPED`.

## Configuration

Each arena file `arenas/<name>.yml` is generated from `prototype/arena.yml`. Key settings:

### Core Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `Lifes` | int | 3 | Deaths before player is kicked. Must be configured (not -1). |
| `Disable_Health_Regen` | boolean | false | Disable natural health regen (potions still work). |
| `Required_Class_Tier` | int | 1 | Minimum class tier to play. |
| `Allow_Own_Equipment` | boolean | false | Let players use own inventory instead of classes. |
| `Natural_Drops` | boolean | false | Allow mobs to drop natural loot. |
| `Random_Respawn_Location` | boolean | false | Randomize respawn point after death. |
| `Open_Class_Menu` | boolean | true | Open class selection on lobby join. |
| `Procedural_Damage` | boolean | true | Enable WorldEdit-based arena damage/restore. |
| `Next_Phase_Mode` | timer/monsters | timer | How phases advance. |
| `Next_Phase_Wait` | time string | 10 seconds | Warm-up between phases. Minimum "1 second". |
| `Mob_Spread` | int | 3 | Radius around spawner to spread mobs. 0 disables. |
| `Mob_Burn_On_Sunlight` | boolean | false | Allow monster sunlight burning and Fire Aspect. |
| `Mob_Limit` | int | 100 | Maximum mobs in region (0-800). |
| `Spawner_Activation_Radius` | int | 40 | Player must be within this radius for spawner to activate. |
| `Explosive_Arrows_Damage_Players` | boolean | true | Whether explosive arrows hurt players. |

### Player_Limit Section

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `Player_Limit.Minimum` | int | 2 | Min players to start (1-100). |
| `Player_Limit.Maximum` | int | 8 | Max players allowed (1-100). |

### Duration Section

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `Duration.Lobby` | time string | 30 seconds | Lobby countdown (10s-1800s). |
| `Duration.Arena` | time string | 5 minutes | Max game duration (10s-7200s). |
| `Duration.Phase` | time string | 30 seconds | Phase duration when using timer mode (10s-7200s). |

### Phase Section

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `Phase.Max_Phase` | int | -1 | Final phase number. -1 = unlimited. If `Arena_End` is set, must be -1. |
| `Phase.PvP` | int | -1 | Phase from which PvP is enabled. -1 = disabled. |
| `Phase.Chest_Refill` | int/list | -1 | Phase(s) to refill chests. Int = every nth phase. List = specific phases. |
| `Phase.Players_End` | int | -1 | Auto-stop when players drop to this count. |
| `Phase.Arena_End` | int | -1 | Arena ends after this phase. |
| `Phase.Arena_End_No_Monsters` | int | -1 | After this phase, arena ends immediately when 0 monsters remain. |

### Interaction Section

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `Interaction.Ignite_Tnts` | boolean | true | Auto-ignite placed TNT. |
| `Interaction.Spawn_Wolves` | boolean | true | Right-click bone to spawn tamed wolf. |
| `Interaction.Launch_Fireballs` | boolean | true | Right-click fire charge to launch fireball. |
| `Interaction.Allow_Breaking` | list | [VINE, LEAVES, LEAVES_2] | Blocks players may break. Use `*` for all. |
| `Interaction.Allow_Placement` | list | [STONE_BUTTON, WOOD_BUTTON] | Blocks players may place. Use `*` for all. |
| `Interaction.Disallow_Auto_Repair` | list | [GOLD_SWORD] | Items that still take damage even with Auto_Repair_Items. |

### Commands Section

Each command hook has three sub-keys: `Player` (run as player), `Player_Console` (run from console per player), `Console` (run once from console). Available hooks:

- `Commands.Start` -- When arena starts (LOBBY -> RUNNING).
- `Commands.Lobby_Start` -- When first player joins and lobby countdown begins.
- `Commands.Phase` -- On each new phase. Use `{phase}` placeholder.
- `Commands.Last_Phase` -- When final phase ends.
- `Commands.Finish` -- When arena finishes gracefully (natural end).
- `Commands.End` -- When arena ends for any reason.
- `Commands.Player_Leave` -- When any player leaves for any reason.

Special command prefixes: `@tell <message>` sends a message to the player. `@connect <server>` sends the player to another BungeeCord server.

### Sound Section

| Key | Default | Format |
|-----|---------|--------|
| `Sound.Player_Join` | ARROW_HIT 1F 0.1F | `<sound_name> <volume> <pitch>` |
| `Sound.Player_Leave` | ENDERDRAGON_DEATH 0.9F 1F | |
| `Sound.Arena_Start` | ENTITY_FIREWORK_LARGE_BLAST_FAR 1F 0.1F | |

### Rewards Section (Per-Arena)

```yaml
Rewards:
  Every:
    5:
    - "iron_ingot:16"
    - "gold_ingot:8"
  At:
    10:
    - "iron_sword"
    - "/cc give physical dungeons 1 {player}"
    30:
    - "golden_apple:1:warrior"
```

Format: `material_name` or `material_name:amount` or `material_name:amount:required_class`. Commands start with `/`.

### Experience Override (Per-Arena)

Arenas can override global experience formulas:

```yaml
Experience:
  Next_Phase: "5 + (5 * {phase})"
  Kill:
    Global: "10 + (5 * {phase})"
    Player: "30 + (6 * {phase})"
    CREEPER: "15 + (5 * {phase})"
```

### Other

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `End_Commands_Delay` | time string | 0 | Delay before Finish/End commands fire. Use if giving items to avoid wipe. |

## Creating an Arena

1. Run `/arena new <name>` -- Creates `arenas/<name>.yml` from prototype, enters edit mode.
2. Run `/arena tools` -- Opens the setup tools menu.
3. Use **Arena Region Point** tool (Emerald) -- Left-click block for primary corner, right-click for secondary corner. Defines the arena cuboid region.
4. Use **Lobby Point** tool (Diamond) -- Click a block inside the region to set the lobby spawn. Must be at least 2 blocks below the region top boundary.
5. Use **Player Spawnpoint** tool (Gold Ingot) -- Click blocks to add player spawn locations. At least one required.
6. Use **Monster Spawnpoint** tool (Iron Ingot) -- Click blocks to add monster spawner locations. Right-click an existing monster spawnpoint while in edit mode to open its mob configuration menu.
7. Run `/arena edit` to leave edit mode.
8. Optionally run `/arena toggle` to enable/disable the arena.

### Readiness Check

An arena is "ready" when all three conditions are met (checked in `SimpleSetup.isReady()`):
- Lobby point is set
- Region has both primary and secondary points
- At least one player spawnpoint exists

## Common Issues & Solutions

**"Arena has lobby point outside of its region"**
The lobby location plus 2 blocks upward must be within the arena region. Move the lobby point lower or expand the region upward.

**Arena does not start / "not enough players"**
Check `Player_Limit.Minimum`. The lobby countdown must complete with at least that many players. Use `/arena start` to force-start from lobby state.

**Players kicked with "no class"**
If `Allow_Own_Equipment` is false and `Give_Random_Class_If_Not_Selected` is false in settings.yml, players without a selected class are kicked. Either enable `Give_Random_Class_If_Not_Selected` or ensure players pick a class during lobby.

**Phases not advancing in monsters mode**
Set `Debug` in settings.yml to `[next-phase]` and check console. Bees and Wolves are only counted as aggressive when angry. Other non-aggressive entities inside the region may be blocking advancement.

**"Lifes" not configured**
Every arena must have `Lifes` set to a positive integer. If it is -1 or missing, players will get an error on join.

**Arena not restoring blocks after game**
Procedural Damage requires WorldEdit, `Procedural_Damage: true` in the arena file, and `Procedural_Damage.Enabled: true` in settings.yml. Snapshots must be taken via `/arena menu`.

**If `Arena_End` and `Max_Phase` are both set**
The plugin forces `Max_Phase` to -1 and logs a warning. Only use one of these.

## Key File Paths

| File | Purpose |
|------|---------|
| `src/main/java/org/mineacademy/corearena/impl/arena/SimpleArena.java` | Core arena lifecycle (join, start, stop, leave) |
| `src/main/java/org/mineacademy/corearena/impl/arena/FeatureArena.java` | Lives, classes, spawns, PvP, interactions |
| `src/main/java/org/mineacademy/corearena/impl/arena/MobArena.java` | Concrete mob arena type |
| `src/main/java/org/mineacademy/corearena/impl/SimpleSettings.java` | Per-arena YAML config loader |
| `src/main/java/org/mineacademy/corearena/impl/SimpleSetup.java` | Arena readiness checks |
| `src/main/java/org/mineacademy/corearena/type/ArenaState.java` | STOPPED, LOBBY, RUNNING enum |
| `src/main/java/org/mineacademy/corearena/type/NextPhaseMode.java` | TIMER, MONSTERS enum |
| `src/main/java/org/mineacademy/corearena/model/ArenaCommands.java` | Command execution for arena hooks |
| `src/main/java/org/mineacademy/corearena/countdown/LaunchCountdown.java` | Lobby countdown |
| `src/main/java/org/mineacademy/corearena/countdown/EndCountdown.java` | Arena duration countdown |
| `src/main/java/org/mineacademy/corearena/countdown/PhaseCountdown.java` | Phase timer |
| `src/main/resources/prototype/arena.yml` | Default arena config template |
| `src/main/java/org/mineacademy/corearena/tool/RegionArenaTool.java` | Region selection tool |
| `src/main/java/org/mineacademy/corearena/tool/LobbyTool.java` | Lobby point tool |
| `src/main/java/org/mineacademy/corearena/tool/SpawnpointPlayerTool.java` | Player spawnpoint tool |
| `src/main/java/org/mineacademy/corearena/tool/SpawnpointMonsterTool.java` | Monster spawnpoint tool |
| `src/main/java/org/mineacademy/corearena/settings/Settings.java` | Global settings loader |
| `src/main/resources/settings.yml` | Global settings file |
