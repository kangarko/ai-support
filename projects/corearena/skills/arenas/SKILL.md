---
name: corearena-arenas
description: 'Arena creation, lifecycle states, per-arena config keys, setup tools, and phase system'
---

# CoreArena - Arenas

## Overview

CoreArena is a Minecraft mob-arena plugin. Each arena is a self-contained instance where players fight waves (phases) of monsters. Arenas follow a strict lifecycle: STOPPED -> LOBBY -> RUNNING -> STOPPED. Configuration lives in individual YAML files under `arenas/<name>.yml`, auto-generated from `prototype/arena.yml`.

## Architecture

### Key Classes

- `SimpleArena` (`impl/arena/SimpleArena.java`) -- Abstract base implementing the `Arena` interface.
- `FeatureArena` (`impl/arena/FeatureArena.java`) -- Extends `SimpleArena`.
- `MobArena` (`impl/arena/MobArena.java`) -- Concrete arena type extending `FeatureArena`.
- `ArenaState` (`type/ArenaState.java`) -- Enum with three values: `STOPPED`, `LOBBY`, `RUNNING`.
- `NextPhaseMode` (`type/NextPhaseMode.java`) -- Enum: `TIMER` (phase advances on timer) or `MONSTERS` (phase advances when all aggressive mobs are killed).
- `SimpleSettings` (`impl/SimpleSettings.java`) -- Loads and holds all per-arena config from `arenas/<name>.yml`.
- `SimpleSetup` (`impl/SimpleSetup.java`) -- Tracks setup readiness: requires lobby point, region (primary + secondary), and at least one player spawn point.
- `SimplePhaseIncremental` (`impl/SimplePhaseIncremental.java`) -- Phase timer implementation.
- `ArenaCommands` (`model/ArenaCommands.java`) -- Holds and executes Player/Player_Console/Console command lists for arena lifecycle hooks.
- `StopCause` (`type/StopCause.java`) -- Enum of reasons an arena can stop: `NATURAL_COUNTDOWN`, `NATURAL_NO_MONSTERS`, `INTERRUPTED_LAST_PLAYER_LEFT`, `INTERRUPTED_COMMAND`, `INTERRUPTED_ERROR`, `CANCELLED_NOT_ENOUGH_PLAYERS`.
- `LeaveCause` (`type/LeaveCause.java`) -- Enum of reasons a player leaves: `COMMAND`, `KILLED`, `ARENA_END`, `DISCONNECT`, `ESCAPED`, `NO_ENOUGH_CLASS`, `NOT_READY`, `ERROR`.

### Lifecycle Flow

1. **STOPPED**: Arena is idle. No players.
2. **Player joins** (`joinPlayer`): Checks permissions (`corearena.command.join.{arena}`), arena not running/full/edited, player not already in another arena, inventory empty (if `Store_Inventories` is false). Teleports player to lobby.
3. **LOBBY**: First join triggers `startLobby()`. Sets state to `LOBBY`, clears entities, runs `Lobby_Start` commands, starts `LaunchCountdown` (configurable via `Duration.Lobby`).
4. **Countdown expires or `/arena start`**: Calls `startArena()`. Checks minimum player count. Sets state to `RUNNING`, cancels lobby countdown, starts `EndCountdown` (configurable via `Duration.Arena`), starts phase timer, assigns classes and spawn points, runs `Start` commands.
5. **RUNNING**: Phases advance per `Next_Phase_Mode`. Monsters spawn. Players fight. Experience is collected. Rewards given per wave config.
6. **Arena ends**: Triggered by countdown expiry, all monsters killed (if `Arena_End_No_Monsters` is set), max phase reached, last player leaving, or `/arena stop`. Calls `stopArena()`: cancels countdowns, resets phase, removes entities, restores snapshot, runs `Finish` commands (if natural end) then `End` commands, removes all players, sets state back to `STOPPED`.

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

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
