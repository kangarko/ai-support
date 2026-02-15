---
name: chests
description: 'Gift, Dated, and Timed chest systems with sign-based creation and protection'
---

# Chest System

## Overview

Winter provides three types of special chests created by placing signs on regular chests. Each chest type has its own sign format, permissions, and opening behavior. Chest ownership is tracked in `data/chests.yml`, and player interaction history (open count, timestamps) is tracked in `data/data.yml`. All chests are protected from unauthorized breaking and expansion.

## Architecture

### Key Classes

- `ChestMatcher` -- Interface defining three methods: `isValidFormat(String[] lines)` for sign format validation, `getValidFormatExample()` for error messages, and `getPermission()` for the required permission node.
- `WinterChest` -- Interface extending `ChestMatcher`.
- `GiftChest` -- Implements `WinterChest`.
- `InfiniteChest` -- Abstract class implementing `WinterChest`.
- `DatedChest` -- Extends `InfiniteChest`.
- `TimedChest` -- Extends `InfiniteChest`.
- `ChestListener` -- Main listener handling four events: `SignChangeEvent` (validates and registers new Winter signs), `PlayerInteractEvent` (opens chests on right-click, checks ownership/permissions/access), `BlockBreakEvent` (protects chests and signs from unauthorized breaking), `BlockPlaceEvent` (protects chests from unauthorized expansion by placing adjacent chests), `InventoryClickEvent` (blocks item manipulation in preview inventory).
- `ChestData` -- Singleton (`data/chests.yml`) storing sign ownership.
- `PlayerData` -- Singleton (`data/data.yml`) storing per-player chest interaction history.
- `GiftSignUtil` -- Utility for finding chests attached to signs and constructing `WinterChest` instances.

### Chest Creation Flow

1. Player places a wall sign on a chest with `[Gift]`, `[Dated]`, or `[Timed]` on line 1.
2. `ChestListener.onSignPlace()` fires on `SignChangeEvent`.
3. The title is stripped of color codes and matched against the registered `validChests` map.
4. Validation: a chest must be adjacent to the sign (`GiftSignUtil.findChest()`), the player needs the correct permission, and the sign format must pass `isValidFormat()`.
5. For Gift chests: if lines 2-4 are empty and `Public.Allow` is true, the public format from settings is applied. Otherwise, receiver names are extracted and the private format with `{receiver_1}`, `{receiver_2}`, `{receiver_3}` placeholders is applied. The title from `Gift_Chest.Title` is set on line 1.
6. `GiftSignUtil.registerSign()` saves the sign owner in `ChestData` and writes the formatted lines.

### Chest Opening Flow

1. Player right-clicks a chest or a sign adjacent to a chest.
2. `ChestListener.onChestOpen()` finds the `WinterChest` via `GiftSignUtil.findChestFull()`.
3. If the player is the owner, they see their own chest contents directly.
4. If sneaking, the interaction is blocked (prevents placing blocks on the chest).
5. For `GiftChest`: public chests open directly; private chests check `canAccess()`; unauthorized players with `winter.chest.admin` can bypass.
6. For `InfiniteChest` (Dated/Timed): calls `onTryOpen()` which validates availability, opens a read-only `InventoryDrawer`, and plays preview or loot sounds. Admin permission bypasses restrictions on failure.

### Chest Protection Flow

- Breaking a chest or sign: owner and admins can break; others get blocked with `chest-illegal-break` / `chest-illegal-break-sign`. On break, sign data is cleaned from `ChestData` and player data from `PlayerData`.
- Placing adjacent chest: owner and admins can expand; others get blocked with `chest-illegal-expand`.
- Preview inventory: all `InventoryClickEvent`s in the preview title are cancelled.

## Common Issues & Solutions

| Issue | Cause | Solution |
|---|---|---|
| [Gift] sign not recognized | `Gift_Chest.Enabled: false` or missing permission | Enable in settings and grant `winter.chest.gift` |
| Sign destroyed on placement | Sign not placed on a chest block, or invalid format | Ensure sign is on a chest face. Check format matches expected pattern |
| Public gift chest not allowed | `Gift_Chest.Public.Allow: false` | Set to `true` or add player names |
| Dated chest says "not ready" | Current date/time outside the range on the sign | Check date format (DD.MM), verify `Default_Year` matches |
| Dated chest: "already opened" | Player already opened max times (2 with preview, 1 without) | This is by design. Admin with `winter.chest.admin` can bypass |
| Timed chest: "not ready" | Cooldown not elapsed | Wait for the configured duration. Check sign line 2 format |
| Timed chest: "can only be looted X times" | Player exceeded max uses on sign line 3 | This is by design. Remove the max uses number for unlimited |
| Can't break a Winter chest | Player is not the owner and lacks `winter.chest.admin` | Grant admin permission or have the owner break it |
| InvalidChestDateException on open | Dated chest sign has a corrupted or invalid date | Break and recreate the sign with valid DD.MM format |
| Year overlap not working | `Default_Year` not set correctly | Set `Default_Year` to the start year (e.g. 2026 for 25.12-03.01) |
| Items can't be taken from preview | Preview mode by design blocks inventory clicks | Open the chest a second time to loot |

## Key File Paths

- Settings: `src/main/resources/settings.yml` (Gift_Chest, Dated_Chest sections)
- Locale: `src/main/resources/lang/en_US.json`
- Chest interface: `src/main/java/org/mineacademy/winter/chest/WinterChest.java`
- Chest matcher: `src/main/java/org/mineacademy/winter/chest/ChestMatcher.java`
- Gift chest: `src/main/java/org/mineacademy/winter/chest/GiftChest.java`
- Infinite chest base: `src/main/java/org/mineacademy/winter/chest/InfiniteChest.java`
- Dated chest: `src/main/java/org/mineacademy/winter/chest/DatedChest.java`
- Timed chest: `src/main/java/org/mineacademy/winter/chest/TimedChest.java`

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
