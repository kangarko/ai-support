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
- `WinterChest` -- Interface extending `ChestMatcher`. Adds `getSign()`, `getChest()`, and `isOwner(Player)` which checks the sign's owner in `ChestData`.
- `GiftChest` -- Implements `WinterChest`. Can be public (empty sign lines, accessible to everyone) or private (player names on lines 2-4, accessible only to named receivers). Public chests require `Gift_Chest.Public.Allow: true`. The `canAccess(Player)` method does case-insensitive name matching against receivers.
- `InfiniteChest` -- Abstract class implementing `WinterChest`. Base for Dated and Timed chests. Provides `onTryOpen(Player)` which checks `canOpen()`, tracks interaction via `PlayerData.onInteract()`, opens a read-only `InventoryDrawer` with the chest's contents, handles preview mode for Dated chests (first open is preview with dragon sound, second open is loot with level-up sound). Contains static `parseDate()` and `parseHour()` utilities.
- `DatedChest` -- Extends `InfiniteChest`. Uses `RangedValue` for day and optional hour ranges. `canOpen()` checks: player has not exceeded use limit (2 with preview, 1 without), current date is in range, current time is in hour range (if specified). Date format: `DD.MM` or `DD.MM-DD.MM` on sign line 2, optional `HH:MM` or `HH:MM-HH:MM` on sign line 3. Uses `Dated_Chest.Default_Year` for year when not specified. Year overlap supported (e.g. 25.12-03.01 wraps by adding 365 days to the end date).
- `TimedChest` -- Extends `InfiniteChest`. Uses a cooldown delay in seconds and an optional max use count. `canOpen()` checks: player has not exceeded max uses (if set), and enough time has passed since last interaction. Time format: `24h`, `40m`, `10s`, etc. on sign line 2, optional max uses integer on sign line 3.
- `ChestListener` -- Main listener handling four events: `SignChangeEvent` (validates and registers new Winter signs), `PlayerInteractEvent` (opens chests on right-click, checks ownership/permissions/access), `BlockBreakEvent` (protects chests and signs from unauthorized breaking), `BlockPlaceEvent` (protects chests from unauthorized expansion by placing adjacent chests), `InventoryClickEvent` (blocks item manipulation in preview inventory).
- `ChestData` -- Singleton (`data/chests.yml`) storing sign ownership. Maps sign locations to owner UUIDs. Methods: `getOwnerOrNull(Sign)`, `removeSign(Sign)`.
- `PlayerData` -- Singleton (`data/data.yml`) storing per-player chest interaction history. Inner class `ChestDataCache` tracks `lastUsed` timestamp and `usedCount`. Inner class `PlayerDataFile` maps chest locations to `ChestDataCache` entries.
- `GiftSignUtil` -- Utility for finding chests attached to signs and constructing `WinterChest` instances. `registerSign()` saves ownership and formats the sign lines. `findChestFull()` searches the chest and all adjacent signs. `constructChest()` parses a sign into the appropriate chest type based on the first line title.

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

## Configuration

### Gift_Chest (settings.yml)

```yaml
Gift_Chest:
  Enabled: true                    # Master toggle for [Gift] sign functionality
  Title: "&8[&fGift&8]"           # Text shown on line 1 of the sign after creation
  Public:
    Allow: true                    # Allow signs without receiver names (open to everyone)
    Format: |-                     # Lines 2-4 for public signs (max 3 lines)
      Click for
      free gifts!
  Private:
    Format: |-                     # Lines 2-4 for private signs, supports placeholders
      {receiver_1}
      {receiver_2}
      {receiver_3}
```

### Dated_Chest (settings.yml)

```yaml
Dated_Chest:
  Preview: true                    # true = 2 opens (first preview, then loot), false = 1 open for loot
  Default_Year: 2026               # Year assumed when sign date has no year (e.g. 24.12-25.12)
```

### Sign Formats

**Gift chest sign:**
```
Line 1: [Gift]
Line 2: PlayerName1     (or empty for public)
Line 3: PlayerName2     (optional)
Line 4: PlayerName3     (optional)
```

**Dated chest sign:**
```
Line 1: [Dated]
Line 2: DD.MM or DD.MM-DD.MM       (required, e.g. 24.12 or 24.12-25.12)
Line 3: HH:MM or HH:MM-HH:MM      (optional, e.g. 17:00-20:00)
Line 4: (unused)
```

**Timed chest sign:**
```
Line 1: [Timed]
Line 2: <duration>                   (required, e.g. 24h, 40m, 10s, 2d)
Line 3: <max_uses>                   (optional integer, omit for unlimited)
Line 4: (unused)
```

### Permissions

| Permission | Description |
|---|---|
| `winter.chest.gift` | Place a [Gift] sign on a chest |
| `winter.chest.dated` | Place a [Dated] sign on a chest |
| `winter.chest.timed` | Place a [Timed] sign on a chest |
| `winter.chest.admin` | Bypass chest protection, open any locked chest, bypass date/time restrictions |

### Locale Messages (lang/en_US.json)

| Key | Context |
|---|---|
| `boxed-chest-open` | Shown when looting an infinite chest (multi-line boxed) |
| `boxed-chest-preview` | Shown when previewing a dated chest (multi-line boxed) |
| `chest-break-admin` | Admin broke a public gift chest |
| `chest-break-admin-sign` | Admin broke a gift chest sign |
| `chest-break-own` | Owner broke their own chest |
| `chest-break-own-sign` | Owner broke their own sign |
| `chest-create-success` | Winter sign placed successfully |
| `chest-dated-limit` | Player already opened this dated chest |
| `chest-dated-not-ready` | Dated chest not yet available (shows date/time range) |
| `chest-expand-own` | Owner expanded a locked gift chest |
| `chest-format-dated` | Expected format hint for [Dated] signs |
| `chest-format-gift` | Expected format hint for [Gift] signs |
| `chest-format-timed` | Expected format hint for [Timed] signs |
| `chest-illegal-access` | Non-receiver tried to open a private gift chest |
| `chest-illegal-break` | Unauthorized player tried to break a chest |
| `chest-illegal-break-sign` | Unauthorized player tried to break a sign |
| `chest-illegal-expand` | Unauthorized player tried to expand a chest |
| `chest-illegal-inventory-click` | Player clicked in a preview inventory |
| `chest-illegal-place` | Player tried to place a block on a Winter chest while sneaking |
| `chest-invalid-format` | Sign has wrong format (includes expected format) |
| `chest-no-player` | Gift sign placed without receivers when public is disabled |
| `chest-no-sign` | Sign placed not adjacent to a chest |
| `chest-open-admin` | Admin viewing a locked chest |
| `chest-open-admin-dated` | Admin bypassed date restriction |
| `chest-open-own` | Owner browsing their own chest |
| `chest-open-private` | Named receiver opening their gift |
| `chest-open-public` | Anyone opening a public gift chest |
| `chest-timed-limit` | Player exceeded max uses for a timed chest |
| `chest-timed-not-ready` | Timed chest cooldown not elapsed (shows remaining time) |
| `part-at`, `part-between`, `part-on` | Localized prepositions for date messages |

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
- Chest listener: `src/main/java/org/mineacademy/winter/listener/ChestListener.java`
- Chest data: `src/main/java/org/mineacademy/winter/model/ChestData.java`
- Player data: `src/main/java/org/mineacademy/winter/model/PlayerData.java`
- Sign utilities: `src/main/java/org/mineacademy/winter/util/GiftSignUtil.java`
- Permissions: `src/main/java/org/mineacademy/winter/model/Permissions.java`
