---
name: corearena-signs-setup
description: 'Sign types, sign creation, edit mode, setup tools, WorldEdit settings, and MySQL config'
---

# CoreArena - Signs & Setup

## Overview

CoreArena uses physical Minecraft signs as interactive elements within and around arenas. There are 7 sign types serving different purposes: joining, leaving, class selection, upgrades, redstone power triggers, a classes menu shortcut, and a rewards menu shortcut. Setup involves edit mode and specialized tools. The plugin also supports WorldEdit for arena snapshot management and MySQL for cross-server data sharing.

## Architecture

### Key Classes

- `SimpleSign` (`impl/SimpleSign.java`) -- Abstract base for all arena signs.
- `SimpleSignJoin` (`impl/SimpleSignJoin.java`) -- Join sign.
- `SimpleSignLeave` (`impl/SimpleSignLeave.java`) -- Leave sign.
- `SimpleSignClass` (`impl/SimpleSignClass.java`) -- Class sign.
- `SimpleSignUpgrade` (`impl/SimpleSignUpgrade.java`) -- Upgrade sign.
- `SimpleSignPower` (`impl/SimpleSignPower.java`) -- Power sign.
- `SimpleSigns` (`manager/SimpleSigns.java`) -- Holds all signs for a single arena, organized by `SignType`.
- `SignsListener` (`listener/SignsListener.java`) -- Bukkit event listener handling sign creation (`SignChangeEvent`), sign clicking (`PlayerInteractEvent`), and sign breaking (`BlockBreakEvent`).
- `ArenaSign.SignType` (`model/ArenaSign.java`) -- Enum: `JOIN`, `LEAVE`, `CLASS`, `UPGRADE`, `POWER`.
- `SimpleSetup` (`impl/SimpleSetup.java`) -- Tracks arena setup state.
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

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
