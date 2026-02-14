---
name: corearena-signs-setup
description: 'Sign types, sign creation, edit mode, setup tools, WorldEdit settings, and MySQL config'
---

# CoreArena - Signs & Setup

## Overview

CoreArena uses physical Minecraft signs as interactive elements within and around arenas. There are 7 sign types serving different purposes: joining, leaving, class selection, upgrades, redstone power triggers, a classes menu shortcut, and a rewards menu shortcut. Setup involves edit mode and specialized tools. The plugin also supports WorldEdit for arena snapshot management and MySQL for cross-server data sharing.

## Architecture

### Key Classes

- `SimpleSign` (`impl/SimpleSign.java`) -- Abstract base for all arena signs. Handles location tracking, variable replacement, state updates, sign removal, and serialization/deserialization. Contains a static factory `deserialize()` that dispatches to the correct subclass.
- `SimpleSignJoin` (`impl/SimpleSignJoin.java`) -- Join sign. When clicked outside arena, joins the player. Displays arena state, player count.
- `SimpleSignLeave` (`impl/SimpleSignLeave.java`) -- Leave sign. When clicked in-game, kicks the player from the arena.
- `SimpleSignClass` (`impl/SimpleSignClass.java`) -- Class sign. When clicked in lobby, gives the associated class to the player (preview mode). When clicked in edit mode, opens class GUI.
- `SimpleSignUpgrade` (`impl/SimpleSignUpgrade.java`) -- Upgrade sign. When clicked during RUNNING state, purchases the upgrade using in-arena levels. Checks phase lock and level cost.
- `SimpleSignPower` (`impl/SimpleSignPower.java`) -- Power sign. Emits a redstone pulse (converts to redstone block for 5 ticks, then back to sign) at specific arena lifecycle events: Lobby, Start, Phase, or End.
- `SimpleSigns` (`manager/SimpleSigns.java`) -- Holds all signs for a single arena, organized by `SignType`. Provides lookup and batch update methods.
- `SignsListener` (`listener/SignsListener.java`) -- Bukkit event listener handling sign creation (`SignChangeEvent`), sign clicking (`PlayerInteractEvent`), and sign breaking (`BlockBreakEvent`).
- `ArenaSign.SignType` (`model/ArenaSign.java`) -- Enum: `JOIN`, `LEAVE`, `CLASS`, `UPGRADE`, `POWER`.
- `SimpleSetup` (`impl/SimpleSetup.java`) -- Tracks arena setup state. Checks lobby, region, and player spawnpoints.
- `SetupManager` (`manager/SetupManager.java`) -- Manages which arenas are being edited and by whom.

### Sign Types

There are 7 sign types users can create. Five are registered internally (JOIN, LEAVE, CLASS, UPGRADE, POWER) and two are unregistered shortcuts (CLASSES, REWARDS) that just open menus when clicked.

| Sign | First Line | Registered | Click Behavior |
|------|-----------|------------|----------------|
| Join | `[arena]` or `[ma]` (the command label) | Yes | Out-of-game: joins player. In-game: nothing. |
| Leave | `[leave]` | Yes | In-game: leaves arena. Out-of-game: nothing. |
| Class | `[class]` | Yes | In lobby: gives class. Edit mode: opens class GUI. |
| Upgrade | `[upgrade]` | Yes | In running arena: purchases upgrade. Edit mode: opens upgrade GUI. |
| Power | `[power]` | Yes | No click action. Emits redstone pulse on lifecycle events. |
| Classes | `[classes]` | No | Opens class selection menu (same as `/arena class`). |
| Rewards | `[rewards]` | No | Opens rewards purchase menu (same as `/arena rewards`). |

## Configuration

### Sign Labels (`settings.yml` -> `Signs.Label`)

These labels define what text goes inside the brackets on the first line of each sign:

| Key | Default | Sign Created With |
|-----|---------|-------------------|
| `Signs.Label.Class` | `class` | `[class]` |
| `Signs.Label.Classes` | `classes` | `[classes]` |
| `Signs.Label.Upgrade` | `upgrade` | `[upgrade]` |
| `Signs.Label.Power` | `power` | `[power]` |
| `Signs.Label.Leave` | `leave` | `[leave]` |
| `Signs.Label.Rewards` | `rewards` | `[rewards]` |

The join sign uses the main command label (e.g., `[arena]` or `[ma]`), not a configurable label.

### Sign Formats (`settings.yml` -> `Signs`)

| Key | Default | Variables |
|-----|---------|-----------|
| `Signs.Join_Sign_Format` | `[&l{arena}&r]\n{state}\n&8{players}/{maxPlayers}` | `{arena}`, `{state}`, `{players}`, `{maxPlayers}` |
| `Signs.Leave_Sign_Format` | `[&lLeave&r]\nClick to leave\n{arena}` | `{arena}` |
| `Signs.Class_Sign_Format` | `[&lClass&r]\n{class}` | `{class}` |
| `Signs.Upgrades_Sign_Format` | `[&4Upgrade&r]\n{upgrade}\n{price}\n&7Click to buy.` | `{upgrade}`, `{price}` |

Power signs use a hardcoded format showing `{type}` (Lobby/Start/Phase/End).

Signs support up to 4 lines maximum.

### Other Sign Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `Signs.Allow_Classes_Sign` | boolean | true | Allow creating the `[classes]` shortcut sign. |

## Creating Signs

### Join Sign

1. Place a sign anywhere in the world.
2. Write `[arena]` (or `[ma]`, whatever the command label is) on the first line.
3. Write the arena name on the second line.
4. The sign auto-formats using `Join_Sign_Format` and dynamically updates with player count and arena state.

The sign must reference an existing arena by name. It does NOT need to be inside the arena region.

### Leave Sign

1. Place a sign inside an arena region (the plugin checks `findArena(block.getLocation())`).
2. Write `[leave]` on the first line.
3. Arena is auto-detected from the sign's location.

### Class Sign

1. Place a sign inside an arena region.
2. Write `[class]` on the first line.
3. Write the class name on the second line.
4. The class must exist. The sign auto-formats.

### Upgrade Sign

1. Place a sign inside an arena region.
2. Write `[upgrade]` on the first line.
3. Write the upgrade name on the second line.
4. Write the level cost (integer) on the third line.
5. The upgrade must exist and cost must be a positive integer.

### Power Sign

1. Place a sign inside an arena region.
2. Write `[power]` on the first line.
3. Write the trigger type on the second line: `Lobby`, `Start`, `Phase`, or `End`.
4. When the matching event fires, the sign block is temporarily replaced with a redstone block for 5 ticks, then restored.

### Classes Sign (Unregistered)

1. Place a sign anywhere.
2. Write `[classes]` on the first line.
3. Right-clicking opens the class selection menu (requires `Allow_Classes_Sign: true`).

### Rewards Sign (Unregistered)

1. Place a sign anywhere.
2. Write `[rewards]` on the first line.
3. Right-clicking opens the rewards purchase menu.

## Edit Mode

Edit mode is toggled with `/arena edit [arena]`. While active:

- The editing player's name is tracked in `SetupManager`.
- A sidebar is shown to the player with setup status.
- Setup tools are rendered (existing spawnpoints, region corners, lobby shown as colored blocks).
- Clicking registered signs in the arena opens their setup/configuration GUIs instead of their normal behavior.
- Right-clicking a monster spawnpoint opens the mob configuration menu for that spawner.
- The arena cannot be joined by players while being edited.
- Only one player can edit an arena at a time.

### Setup Tools

Obtained via `/arena tools` menu. Each tool is a specially-named item:

| Tool | Item | Mask Block | Color | Left Click | Right Click | Break |
|------|------|------------|-------|------------|-------------|-------|
| Arena Region Point | Emerald | Emerald Block | Green | Set primary corner | Set secondary corner | Remove point |
| Lobby Point | Diamond | Diamond Block | Aqua | Set lobby location | Set lobby location | Remove lobby |
| Player Spawnpoint | Gold Ingot | Gold Block | Gold | Add player spawn | Add player spawn | Remove spawn |
| Monster Spawnpoint | Iron Ingot | Iron Block | White | Add monster spawn | Add monster spawn | Remove spawn |

Tools visualize existing points by temporarily rendering their mask blocks. The region tool also draws a wireframe boundary when both corners are set (30-second visualization).

All tools require the `corearena.tools` permission and the arena must be in edit mode.

## WorldEdit Integration (`settings.yml` -> `WorldEdit`)

Used for procedural damage: saving initial/damaged arena snapshots and restoring them between games.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `WorldEdit.Block_Bulk_Restore_Amount` | int | 100000 | Blocks restored per batch to prevent lag. |
| `WorldEdit.Wait_Period` | time | 30 ticks | Delay between restore batches. |
| `WorldEdit.Close_Stream` | boolean | false | Set true for memory leak issues. Set false for "Stream Closed" IOException. |

Snapshots are managed through `/arena menu <arenaname>` GUI.

## MySQL Configuration (`settings.yml` -> `MySQL`)

Allows sharing player data (nuggets, tiers, etc.) across multiple servers.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `MySQL.Enabled` | boolean | false | Enable MySQL storage. |
| `MySQL.Delay_Ticks` | int | 10 | Sync delay in ticks. Adjust based on MySQL latency. Rule: (ms / 50) + 6 ticks reserve. |
| `MySQL.Host` | string | localhost | Database host. |
| `MySQL.Database` | string | minecraft | Database name. |
| `MySQL.Port` | string | 3306 | Database port. |
| `MySQL.User` | string | (empty) | Database user. |
| `MySQL.Password` | string | (empty) | Database password. |
| `MySQL.Connector_Advanced` | string | `jdbc:mysql://{host}:{port}/{database}?autoReconnect=true` | JDBC connection string template. |

Debug MySQL sync timing by setting `Debug` to `[mysql]` in settings.yml.

## Common Issues & Solutions

**Sign breaks immediately after placing**
The sign's second line references a non-existent arena/class/upgrade, or the sign is placed outside any arena region (for types that require it: leave, class, upgrade, power). The block breaks and an error message is shown.

**Join sign not updating player count**
Join signs update on player join and leave events. If the sign block was physically changed or the chunk was unloaded, the sign state reference may be stale. Check that the sign block is still intact.

**Power sign not resetting back to sign**
The power sign converts to a redstone block and back after 5 ticks. If the server crashes during those 5 ticks, the block may remain as redstone. Manually replace it with a sign and recreate.

**"The sign refers to a non-existing arena class/upgrade"**
The class or upgrade was deleted after the sign was created. Break the sign and recreate it.

**Upgrade sign says "locked" or "not enough levels"**
The upgrade's `Available_From_Phase` has not been reached yet, or the player's in-arena level is below the sign's cost value (third line when creating the sign).

**Edit mode tools not showing existing points**
Make sure the arena is in edit mode (`/arena edit <name>`) and you have `corearena.tools` permission. Tools render existing points when entering edit mode or when focused in the hotbar.

**WorldEdit restore causing lag**
Lower `Block_Bulk_Restore_Amount` and/or increase `Wait_Period`. Larger arenas need more time to restore, so ensure the lobby duration is long enough.

**MySQL out of sync between servers**
Set `Debug` to `[mysql]` and check the "Updating MySQL data for x took y ms" log. Set `Delay_Ticks` to `(ms / 50) + 6`.

## Key File Paths

| File | Purpose |
|------|---------|
| `src/main/java/org/mineacademy/corearena/impl/SimpleSign.java` | Abstract sign base, factory deserializer |
| `src/main/java/org/mineacademy/corearena/impl/SimpleSignJoin.java` | Join sign implementation |
| `src/main/java/org/mineacademy/corearena/impl/SimpleSignLeave.java` | Leave sign implementation |
| `src/main/java/org/mineacademy/corearena/impl/SimpleSignClass.java` | Class sign implementation |
| `src/main/java/org/mineacademy/corearena/impl/SimpleSignUpgrade.java` | Upgrade sign implementation |
| `src/main/java/org/mineacademy/corearena/impl/SimpleSignPower.java` | Power sign with redstone pulse |
| `src/main/java/org/mineacademy/corearena/manager/SimpleSigns.java` | Per-arena sign registry |
| `src/main/java/org/mineacademy/corearena/listener/SignsListener.java` | Sign creation, click, and break handling |
| `src/main/java/org/mineacademy/corearena/model/ArenaSign.java` | ArenaSign interface and SignType enum |
| `src/main/java/org/mineacademy/corearena/impl/SimpleSetup.java` | Arena setup readiness checks |
| `src/main/java/org/mineacademy/corearena/manager/SetupManager.java` | Edit mode tracking |
| `src/main/java/org/mineacademy/corearena/tool/RegionArenaTool.java` | Region selection tool |
| `src/main/java/org/mineacademy/corearena/tool/LobbyTool.java` | Lobby point tool |
| `src/main/java/org/mineacademy/corearena/tool/SpawnpointPlayerTool.java` | Player spawnpoint tool |
| `src/main/java/org/mineacademy/corearena/tool/SpawnpointMonsterTool.java` | Monster spawnpoint tool |
| `src/main/java/org/mineacademy/corearena/tool/SelectorTool.java` | Abstract base for all setup tools |
| `src/main/java/org/mineacademy/corearena/settings/Settings.java` | Signs, WorldEdit, MySQL settings |
| `src/main/resources/settings.yml` | Global settings file |
