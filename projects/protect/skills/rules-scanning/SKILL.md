---
name: rules-scanning
description: 'Rule engine, material matching, operators, groups, scan triggers, and default rules'
---

# Rules & Scanning Engine

## Overview

Protect scans player inventories and containers against a set of user-defined rules written in `.rs` files inside the `rules/` folder. Each rule matches materials using a high-performance FastMatcher, then applies a chain of require/ignore/check/then operators to filter and act on items. Rules can reference reusable operator groups defined in `group.rs`.

## Architecture

### Key Classes

- `Rule` (`operator/Rule.java`) - A single rule parsed from a `.rs` file. Holds a `FastMatcher` for the `match` line, a unique `name`, and an optional `Group` reference. Contains `RuleCheck` inner class that performs the actual item evaluation.
- `Rules` (`operator/Rules.java`) - Singleton that loads all `.rs` files (except `group.rs`) from the `rules/` folder. Holds the ordered list of all rules. Rules are evaluated top-to-bottom.
- `Group` (`operator/Group.java`) - A named collection of operators that can be reused across multiple rules. Defined in `group.rs`.
- `Groups` (`operator/Groups.java`) - Singleton that loads groups from `rules/group.rs`. Groups are loaded before rules so rules can reference them.
- `ProtectOperator` (`operator/ProtectOperator.java`) - Abstract base extending `Operator`. Defines all Protect-specific operators (require amount, require name, ignore material, check stack, then confiscate, etc.). Contains `ProtectCheck` inner class with the filtering logic.
- `Operator` (`operator/Operator.java`) - Abstract base for all operators. Defines common operators (require/ignore perm, gamemode, world, region, playtime, key, script; then command, console, log, kick, toast, notify, discord, warn, abort; meta: dont log, dont verbose, disabled, begins, expires, delay).
- `FastMatcher` (`model/FastMatcher.java`) - High-performance pattern matcher with four modes: wildcard start (`*SUFFIX`), wildcard end (`PREFIX*`), exact (`"EXACT"`), and contains. Supports pipe `|` for OR. Prefix `* ` (star space) to use full Java regex.
- `ScanListener` (`listener/ScanListener.java`) - Bukkit listener that triggers scans on join, death, world change, inventory open, item click, item spawn, and command execution based on `settings.yml` Scan section.
- `ScanCause` (`model/ScanCause.java`) - Enum of scan triggers: `MANUAL`, `PERIOD`, `PLAYER_JOIN`, `PLAYER_DEATH`, `WORLD_CHANGE`, `COMMAND`, `INVENTORY_OPEN`, `ITEM_CLICK`, `ITEM_SPAWN`.

### Rule File Format

Each rule in a `.rs` file starts with `match` and must have a unique `name`. Everything between two `match` lines belongs to one rule. Comments start with `#`. You can create as many `.rs` files as needed in the `rules/` folder.

```
match <material_pattern>
name <unique-name>
<operators...>
```

### Group File Format

Groups are defined in `rules/group.rs`. A group starts with `group <name>` and contains operators. Rules reference groups with `group <name>`.

```
group <name>
<operators...>
```

When a rule references a group, the rule's own operators execute first, then the group's operators execute if the group's own canFilter conditions pass.

## Material Matching (FastMatcher)

The `match` line uses FastMatcher, a high-performance alternative to regex.

| Pattern | Mode | Example | Matches |
|---------|------|---------|---------|
| `*SUFFIX` | Ends with | `*_SWORD` | `DIAMOND_SWORD`, `IRON_SWORD` |
| `PREFIX*` | Starts with | `DIAMOND_*` | `DIAMOND_SWORD`, `DIAMOND_BLOCK` |
| `"EXACT"` | Exact match | `"BEDROCK"` | Only `BEDROCK` |
| `TEXT` | Contains | `DIAMOND` | `DIAMOND_SWORD`, `DIAMOND_BLOCK`, `DIAMOND` |
| `*` | Match all | `*` | Every material |
| `A\|B` | OR | `"DIAMOND"\|"EMERALD"` | `DIAMOND` or `EMERALD` |
| `* ^regex` | Full regex | `* ^DIAMOND_(SWORD\|HOE)` | `DIAMOND_SWORD`, `DIAMOND_HOE` |

Pipe `|` separates multiple patterns where any match counts. You can combine modes with pipe: `"BEDROCK"\|"BARRIER"\|COMMAND*`.

## Protect-Specific Operators (ProtectOperator.java)

### Require Operators (item must meet condition to trigger the rule)

| Operator | Syntax | Description |
|----------|--------|-------------|
| require amount | `require amount <number>` | Item stack size must be >= number |
| require cause | `require cause <cause1\|cause2>` | Only trigger on specific scan causes (pipe-separated ScanCause values) |
| require name | `require name <pattern>` | Item display name (color stripped) must match FastMatcher pattern |
| require name length | `require name length <number>` | Item display name (color stripped) must be >= characters |
| require lore | `require lore <text>` | Item lore (joined with `\|`, color stripped) must equal text |
| require lore length | `require lore length <number>` | Item lore total length must be >= characters |
| require durability | `require durability <math>` | Item durability must match math expression (e.g., `>10`, `5-20`) |
| require potion amount | `require potion amount <number>` | Potion must have >= custom effects |
| require potion duration | `require potion duration <ticks>` | Potion effect duration must be >= ticks |
| require potion amplifier | `require potion amplifier <number>` | Potion effect amplifier must be >= number |
| require enchant level | `require enchant level <number>` | At least one enchantment level must be >= number |
| require tag length | `require tag length <number>` | Item NBT tag string length must be >= number |
| require persistent tag | `require persistent tag <key> [value]` | Item must have persistent data key, optionally matching value |

### Ignore Operators (skip the rule if condition is met)

| Operator | Syntax | Description |
|----------|--------|-------------|
| ignore cause | `ignore cause <cause1\|cause2>` | Skip if scan cause matches (pipe-separated) |
| ignore tag | `ignore tag <nbt_tag_name>` | Skip if item has this NBT tag |
| ignore material | `ignore material <pattern>` | Skip if material matches FastMatcher pattern (pipe-separated) |
| ignore inventory title | `ignore inventory title <pattern>` | Skip if container title matches FastMatcher pattern |
| ignore inventory amount | `ignore inventory amount <number>` | Skip if total count of this material across all slots is <= number. Used with `then confiscate excess` |
| ignore enchantlevel | `ignore enchantlevel <number>` | When using `check enchant too-high`, ignore enchants at or below this level |
| ignore enchant | `ignore enchant <name1\|name2>` | Skip if item has any of these enchantments (pipe-separated) |

### Check Operators (built-in checks)

| Operator | Syntax | Description |
|----------|--------|-------------|
| check stack size | `check stack size` | Triggers if stack amount > item's natural max stack size |
| check enchant not-applicable | `check enchant not-applicable` | Triggers if any enchant cannot naturally apply to the item |
| check enchant too-high | `check enchant too-high` | Triggers if any enchant level exceeds vanilla max level |

### Then Operators (actions when rule matches)

| Operator | Syntax | Description |
|----------|--------|-------------|
| then confiscate | `then confiscate` | Remove the entire item stack from the slot. Aliases: `then take`, `then deny` |
| then confiscate excess | `then confiscate excess` | Remove only the amount exceeding the `ignore inventory amount` limit across all slots |
| then clone | `then clone` | Mark the item with a "cloned" NBT tag so it is ignored on future scans. Used to silently tag suspicious items |
| then disenchant | `then disenchant` | Remove all enchantments from the item |
| then nerf | `then nerf` | Lower enchantments exceeding vanilla max to their vanilla max level. Only works with `check enchant too-high` |

## Common Base Operators (Operator.java)

These operators are available on both rules and groups.

### Require/Ignore (filter conditions)

| Operator | Syntax | Description |
|----------|--------|-------------|
| require perm | `require perm <permission> [deny message]` | Rule only applies if player has permission. Optional message sent when lacking it |
| require script | `require script <JavaScript>` | Rule only applies if JS returns true. Access `nbt` variable for NBTItem |
| require gamemode | `require gamemode <mode1\|mode2>` | Only apply in these gamemodes |
| require world | `require world <world1\|world2>` | Only apply in these worlds |
| require region | `require region <region1\|region2>` | Only apply in these Foundation regions |
| require playtime | `require playtime <time>` | Only apply if player's playtime >= time (e.g., `2 hours`) |
| require key | `require key <name> [JS condition]` | Only apply if player has stored rule data key, optionally matching JS condition with `value` variable |
| ignore perm | `ignore perm <permission>` | Skip rule if player has this permission |
| ignore script | `ignore script <JavaScript>` | Skip rule if JS returns true |
| ignore gamemode | `ignore gamemode <mode1\|mode2>` | Skip in these gamemodes |
| ignore world | `ignore world <world1\|world2>` | Skip in these worlds |
| ignore region | `ignore region <region1\|region2>` | Skip in these Foundation regions |
| ignore playtime | `ignore playtime <time>` | Skip if player's playtime > time |
| ignore key | `ignore key <name> [JS condition]` | Skip if player has stored rule data key matching condition |

### Then (actions)

| Operator | Syntax | Description |
|----------|--------|-------------|
| then command | `then command <cmd>` | Run command as the player. Pipe `\|` for multiple |
| then console | `then console <cmd>` | Run command as console. Pipe `\|` for multiple |
| then log | `then log <message>` | Print message to server console. Pipe `\|` for multiple |
| then kick | `then kick <message>` | Kick the player with message |
| then toast | `then toast <material> <style> <message>` | Show toast/advancement notification. Styles: TASK, GOAL, CHALLENGE |
| then notify | `then notify <permission> <message>` | Send message to all online players with given permission |
| then discord | `then discord <channel> <message>` | Send message to a DiscordSRV channel |
| then write | `then write <file> <message>` | Append message to a log file |
| then fine | `then fine <amount>` | Withdraw money via Vault |
| then sound | `then sound <sound> [volume] [pitch]` | Play a sound to the player |
| then title | `then title <title>\|<subtitle>\|[fadeIn]\|[stay]\|[fadeOut]` | Show title and subtitle |
| then actionbar | `then actionbar <message>` | Show action bar message |
| then bossbar | `then bossbar <color> <overlay> <seconds> <message>` | Show boss bar |
| then warn | `then warn <message>` | Send chat message to the player. Aliases: `then alert`, `then message`. Pipe `\|` for multiple lines |
| then abort | `then abort` | Stop evaluating further rules below this one |
| save key | `save key <name> <JavaScript>` | Store a value in the player's rule data |

### Meta Operators

| Operator | Syntax | Description |
|----------|--------|-------------|
| dont log | `dont log` | Exempt this rule from database logging |
| dont verbose | `dont verbose` | Suppress console verbose output for this rule |
| disabled | `disabled` | Completely disable this rule without deleting it |
| begins | `begins <date>` | Rule only active after this date |
| expires | `expires <date>` | Rule only active before this date |
| delay | `delay <amount> <unit> [message]` | Global cooldown between rule triggers (e.g., `delay 5 seconds`) |
| player delay | `player delay <amount> <unit> [message]` | Per-player cooldown between rule triggers |

## Configuration (settings.yml)

### Scan Section

Controls what triggers inventory scanning:

| Key | Default | Description |
|-----|---------|-------------|
| `Scan.Player_Join` | `true` | Scan on player join |
| `Scan.Player_Death` | `false` | Scan on death |
| `Scan.World_Change` | `false` | Scan on world change |
| `Scan.Inventory_Open` | `true` | Scan containers on open |
| `Scan.Item_Use` | Potions, spawn eggs, fireworks | Scan when right/left clicking these materials |
| `Scan.Item_Spawn` | `false` | Scan dropped/spawned items |
| `Scan.Command` | `[]` | Scan when these commands are issued (starts-with, case insensitive) |
| `Scan.Periodic` | `none` | Periodic scan interval (e.g., `1 hour`, `15 minutes`) |

### Rules Section

| Key | Default | Description |
|-----|---------|-------------|
| `Rules.Verbose` | `true` | Print rule match details to console |
| `Rules.Broadcast` | `true` | Notify players with `protect.notify.item` on match |
| `Rules.Broadcast_Format` | `&8[&c{rule_name}&8] ...` | Format for broadcast message |
| `Rules.Discord_Channel` | `none` | DiscordSRV channel for alerts |
| `Rules.Discord_Format` | `[{server_name}] ...` | Format for Discord alerts |

## Default Rules (main.rs)

The plugin ships with these rules:

1. **unnatural-stack** - Confiscates items exceeding their natural max stack size (e.g., 64x Diamond Sword)
2. **over-64** - Confiscates any stack of 65+
3. **survival-only** - Confiscates creative-only blocks (bedrock, barriers, command blocks, portals) outside creative mode
4. **valuable-block** - Limits diamond/emerald blocks to 64 per container, confiscates excess
5. **valuable-block-beginner** - Limits diamond/emerald blocks to 1 for beginners (group)
6. **valuable-beginner** - Limits diamonds/emeralds to 32 for beginners (group)
7. **impossible-beginner** - Confiscates dragon eggs/beacons for beginners (group)
8. **valuable** - Limits diamonds/emeralds to 256 per container
9. **iron-block** - Limits iron blocks to 3000 per container
10. **gold-block** - Limits gold blocks to 1500 per container
11. **redstone-block** - Limits redstone blocks to 2000 per container
12. **lapis-block** - Limits lapis blocks to 2000 per container
13. **dragon-egg** - Limits dragon eggs to 1 per container
14. **beacon** - Limits beacons to 5 per container
15. **enchanted-apple** - Limits enchanted golden apples to 16 per container
16. **name-too-long** - Confiscates items with display names longer than 64 characters (Wurst crash nametag)
17. **nbt-too-long** - Confiscates items with NBT tags longer than 2048 characters, ignoring player heads (Wurst crash chest)
18. **too-many-potions** - Confiscates potions with 2+ custom effects
19. **level-too-high** - Confiscates potions with amplifier >= 4
20. **enchant-not-applicable** - Confiscates items with enchantments that cannot naturally apply
21. **enchant-too-high** - Confiscates items with enchantments exceeding vanilla max levels

The default group **beginner** (in `group.rs`) applies to players with less than 2 hours of playtime who do not have `protect.bypass.beginner` permission and are not in creative mode. It uses `then confiscate excess`.

## Common Issues & Solutions

1. **Rule not triggering** - Ensure the material name matches exactly (case sensitive, use `UPPER_CASE` Bukkit names). Check `Debug: [scan, operator]` in settings.yml. Verify the rule has a unique `name`. Check that global Ignore settings are not suppressing the scan.
2. **Items from custom plugins being confiscated** - Use `ignore tag <tag>`, `ignore material <pattern>`, or enable `Ignore.Custom_Persistent_Tags: true` in settings.yml. Use `/protect iteminfo nbt` to inspect the item's NBT data.
3. **Rule name error** - Rule names cannot contain spaces. Each rule in the entire `rules/` folder must have a globally unique name.
4. **Group not found** - Groups must be defined in `group.rs` and loaded before rules. Verify the group name in the rule matches exactly.
5. **Performance concerns** - FastMatcher is optimized for speed. Avoid `* ^regex` patterns when possible. Use exact matches (`"MATERIAL"`) or wildcard patterns instead.
6. **confiscate excess not working** - You must pair `then confiscate excess` with `ignore inventory amount <number>`. The amount is counted across all slots in the inventory being scanned.
7. **Scan not running** - Check `Scan` section in settings.yml. Verify the trigger is enabled. Players with `protect.bypass.scan` or OPs (if `Ignore.Ops: true`) are skipped.
8. **mcMMO items being confiscated** - Items with "mcMMO Ability Tool" lore are automatically skipped. The plugin also checks `McMMOHook.isUsingAbility()`.

## Key File Paths

- `src/main/resources/rules/main.rs` - Default rules
- `src/main/resources/rules/group.rs` - Default groups
- `src/main/java/org/mineacademy/protect/operator/Rule.java` - Rule class and RuleCheck
- `src/main/java/org/mineacademy/protect/operator/Rules.java` - Rule loader singleton
- `src/main/java/org/mineacademy/protect/operator/Group.java` - Group class
- `src/main/java/org/mineacademy/protect/operator/Groups.java` - Group loader singleton
- `src/main/java/org/mineacademy/protect/operator/ProtectOperator.java` - Protect-specific operators and filtering logic
- `src/main/java/org/mineacademy/protect/operator/Operator.java` - Common base operators
- `src/main/java/org/mineacademy/protect/model/FastMatcher.java` - Material matching engine
- `src/main/java/org/mineacademy/protect/model/ScanCause.java` - Scan trigger enum
- `src/main/java/org/mineacademy/protect/listener/ScanListener.java` - Event-based scan triggers
- `src/main/resources/settings.yml` - Scan and Rules configuration sections
