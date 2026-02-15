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
- `ProtectOperator` (`operator/ProtectOperator.java`) - Abstract base extending `Operator`. Defines all Protect-specific operators (require amount, require name, ignore material, check stack, then confiscate, etc.). Contains `ProtectCheck` inner...
- `Operator` (`operator/Operator.java`) - Abstract base for all operators. Defines common operators (require/ignore perm, gamemode, world, region, playtime, key, script; then command, console, log, kick, toast, notify, discord, warn, abort; meta:...
- `FastMatcher` (`model/FastMatcher.java`) - High-performance pattern matcher with four modes: wildcard start (`*SUFFIX`), wildcard end (`PREFIX*`), exact (`"EXACT"`), and contains. Supports pipe `|` for OR. Prefix `* ` (star space) to use full Java...
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

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
