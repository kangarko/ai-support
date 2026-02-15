---
name: worldedit-config
description: 'WorldEdit limits, global ignore settings, after-scan actions, rules config, regions, tools, and debug'
---

# WorldEdit Limits & General Configuration

## Overview

Protect integrates with WorldEdit to limit the number of blocks staff can set per operation and restrict specific materials. The plugin also provides a comprehensive global ignore system to exclude certain players, worlds, gamemodes, items, and inventories from scanning. After-scan hooks run commands on confiscation/clone events. The Rules section controls verbose output, broadcasts, and Discord integration for all rule matches.

## Architecture

### Key Classes

- `WorldEditHook` (`hook/WorldEditHook.java`) - Hooks into WorldEdit operations to enforce `Total_Limit` and `Block_Limit` settings. Checks `protect.bypass.worldedit` and `protect.group.{group}` permissions.
- `Settings.WorldEdit` (`settings/Settings.java`) - Loads WorldEdit configuration: `ENABLED`, `TOTAL_GROUP_LIMIT` (map of group name to block count), `BLOCK_LIMIT` (map of lowercase material name to max count or 0 for banned), `WAIT_THRESHOLD`.
- `Settings.Ignore` (`settings/Settings.java`) - Loads global ignore settings: `OPS`, `GAMEMODES`, `WORLDS`, `METADATA_PLAYER`, `METADATA_ITEM`, `CUSTOM_DISPLAY_NAME`, `CUSTOM_LORE`, `CUSTOM_PERSISTENT_TAGS`, `CUSTOM_MODEL_DATA`, `MATERIALS`,...
- `Settings.AfterScan` (`settings/Settings.java`) - Loads after-scan command lists: `CONFISCATE_CONSOLE_COMMANDS`, `CONFISCATE_PLAYER_COMMANDS`, `CLONE_CONSOLE_COMMANDS`, `CLONE_PLAYER_COMMANDS`.
- `Settings.Rules` (`settings/Settings.java`) - Loads rules display settings: `VERBOSE`, `BROADCAST`, `BROADCAST_FORMAT`, `DISCORD_CHANNEL`, `DISCORD_FORMAT`.
- `Rule.RuleCheck` (`operator/Rule.java`) - The inner class that enforces global Ignore settings before evaluating individual rules. Checks `Ignore.OPS`, `Ignore.GAMEMODES`, `Ignore.WORLDS`, `Ignore.METADATA_PLAYER`, bypass permission, McMMO ability...

## Common Issues & Solutions

1. **WorldEdit limits not applying** - Verify `WorldEdit.Enabled: true` and restart the server. Check that the player does not have `protect.bypass.worldedit`. Ensure the player has the correct `protect.group.{group}` permission for Total_Limit.
2. **Material not recognized in Block_Limit** - Use the Bukkit material name (see https://mineacademy.org/material). Legacy names are resolved via CompMaterial. Invalid names are logged as errors on startup.
3. **Custom plugin items being confiscated** - Enable `Custom_Persistent_Tags: true` (default). If the plugin does not set persistent tags, use `Metadata_Item` with the plugin's namespace, or use rule-level `ignore tag` operators. Use `/protect iteminfo nbt` to inspect.
4. **World name error on startup** - `Ignore.Worlds` validates world names on load. Ensure all listed worlds are loaded by the time Protect starts. Move Protect after world management plugins in load order.
5. **After_Scan commands not running** - These only fire for `then confiscate`, `then confiscate excess`, and `then clone` actions. Regular rule operators like `then command` run directly from the rule. After_Scan commands execute in the Rule.RuleCheck after the item is processed.
6. **Verbose output too noisy** - Add `dont verbose` to individual rules, or set `Rules.Verbose: false` globally.
7. **Broadcast messages duplicating** - The `ProtectCheck` class tracks already-sent notify messages per scan to prevent duplication. If seeing duplicates, check if multiple scans are triggering simultaneously (e.g., join + inventory open).
8. **Register_Regions/Register_Tools performance** - Only enable these if you actively use Foundation regions with `require/ignore region` operators. Register_Tools adds a slight tick overhead for tool handling.

## Key File Paths

- `src/main/resources/settings.yml` - All configuration (WorldEdit, Ignore, After_Scan, Rules sections)
- `src/main/java/org/mineacademy/protect/settings/Settings.java` - Settings class with all config loading
- `src/main/java/org/mineacademy/protect/hook/WorldEditHook.java` - WorldEdit integration
- `src/main/java/org/mineacademy/protect/operator/Rule.java` - RuleCheck applies Ignore settings in `filter()` and `check0()` methods; runs After_Scan commands in `checkPlayerInventory()`
- `src/main/java/org/mineacademy/protect/model/Permissions.java` - `protect.group.{group_name}` permission for WorldEdit groups
- `src/main/java/org/mineacademy/protect/listener/ScanListener.java` - References Ignore settings for inventory open filtering

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
