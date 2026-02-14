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
- `Settings.Ignore` (`settings/Settings.java`) - Loads global ignore settings: `OPS`, `GAMEMODES`, `WORLDS`, `METADATA_PLAYER`, `METADATA_ITEM`, `CUSTOM_DISPLAY_NAME`, `CUSTOM_LORE`, `CUSTOM_PERSISTENT_TAGS`, `CUSTOM_MODEL_DATA`, `MATERIALS`, `INVENTORY_TYPES`, `INVENTORY_TITLES`.
- `Settings.AfterScan` (`settings/Settings.java`) - Loads after-scan command lists: `CONFISCATE_CONSOLE_COMMANDS`, `CONFISCATE_PLAYER_COMMANDS`, `CLONE_CONSOLE_COMMANDS`, `CLONE_PLAYER_COMMANDS`.
- `Settings.Rules` (`settings/Settings.java`) - Loads rules display settings: `VERBOSE`, `BROADCAST`, `BROADCAST_FORMAT`, `DISCORD_CHANNEL`, `DISCORD_FORMAT`.
- `Rule.RuleCheck` (`operator/Rule.java`) - The inner class that enforces global Ignore settings before evaluating individual rules. Checks `Ignore.OPS`, `Ignore.GAMEMODES`, `Ignore.WORLDS`, `Ignore.METADATA_PLAYER`, bypass permission, McMMO ability status, `Ignore.MATERIALS`, `Ignore.CUSTOM_DISPLAY_NAME`, `Ignore.CUSTOM_LORE`, `Ignore.CUSTOM_PERSISTENT_TAGS`, `Ignore.CUSTOM_MODEL_DATA`, `Ignore.METADATA_ITEM`.

## Configuration (settings.yml)

### WorldEdit Section

Controls WorldEdit integration. Requires a server restart to toggle `Enabled`.

```yaml
WorldEdit:
  Enabled: true
  Total_Limit:
    vip: 1_000
    moderators: 20_000
  Block_Limit: [CHEST, TRAPPED_CHEST, BEDROCK-512, ...]
  Wait_Threshold: 30 seconds
```

#### Total_Limit (Per-Group Block Limits)

A map of group names to maximum block counts per WorldEdit operation. Players need the `protect.group.{group_name}` permission to be placed in a group. Groups are checked in order (sorted by value) and the first matching group's limit applies. Players without any group permission have no total limit.

Example: A player with `protect.group.vip` can set at most 1,000 blocks per operation. A player with `protect.group.moderators` can set 20,000.

This is NOT related to rule groups in `group.rs`. This uses the `protect.group.{group_name}` permission defined in `Permissions.java`.

#### Block_Limit (Per-Material Restrictions)

A list of materials that are restricted or banned from WorldEdit operations. Two formats:

| Format | Example | Meaning |
|--------|---------|---------|
| `MATERIAL` | `CHEST` | Completely banned from WorldEdit |
| `MATERIAL-<amount>` | `BEDROCK-512` | Maximum of 512 per operation |

Default banned materials include containers (CHEST, FURNACE, HOPPER, etc.), creative-only blocks (BEDROCK, BARRIER, MOB_SPAWNER), luxury blocks with limits (DIAMOND_BLOCK-64, EMERALD_BLOCK-64, TNT-24), and physics-affected blocks that freeze servers when mass-placed (RAILS, LEVER, TORCH, CROPS, etc.).

#### Wait_Threshold

If a player exceeds any block limit, they must wait this duration before using restricted materials again. Default: `30 seconds`. This prevents rapid bypassing with `//replace` or similar commands.

#### Bypass Permission

`protect.bypass.worldedit` - Bypasses all WorldEdit restrictions (Total_Limit and Block_Limit). Note: This is all-or-nothing for performance reasons since some operations work with thousands of items.

### Ignore Section

Global settings that determine which players, items, and inventories are excluded from ALL rule scanning.

```yaml
Ignore:
  Ops: false
  Gamemodes: []
  Worlds: []
  Metadata_Player: [CoreArena_Arena]
  Metadata_Item: [CoreArena_ExpDrop]
  Custom_Display_Name: false
  Custom_Lore: true
  Custom_Persistent_Tags: true
  Custom_Model_Data: true
  Materials: []
  Inventory_Types: [ANVIL]
  Inventory_Titles: ["Custom Inventory Name"]
```

| Key | Default | Description |
|-----|---------|-------------|
| `Ops` | `false` | If true, OP players are never scanned. If false, staff need explicit `protect.bypass.scan` permission |
| `Gamemodes` | `[]` | List of gamemodes to skip entirely. Available: SURVIVAL, CREATIVE, ADVENTURE, SPECTATOR. Warning: creative mode allows hacked items, use rule-level `ignore gamemode creative` instead |
| `Worlds` | `[]` | World names to skip. Must be valid loaded worlds or throws error on startup |
| `Metadata_Player` | `[CoreArena_Arena]` | Skip players with these Bukkit metadata keys (`Player#hasMetadata`) |
| `Metadata_Item` | `[CoreArena_ExpDrop]` | Skip items/dropped entities with these metadata keys. For ItemStacks checks persistent data container (MC 1.14+), for dropped items also checks temporary metadata |
| `Custom_Display_Name` | `false` | Skip items with any custom display name. Warning: hacked clients like Wurst add custom names to crash items. Prefer rule-level ignore operators instead |
| `Custom_Lore` | `true` | Skip items with any custom lore. Typically safe since only plugins set lore |
| `Custom_Persistent_Tags` | `true` | Skip items with any persistent data container keys (MC 1.16+). Prevents confiscating items from custom plugins |
| `Custom_Model_Data` | `true` | Skip items with custom model data (MC 1.14+) |
| `Materials` | `[]` | Exact material names to skip globally. Available at https://mineacademy.org/material |
| `Inventory_Types` | `[ANVIL]` | Container types to skip when scanning on inventory open. Values from Bukkit InventoryType enum |
| `Inventory_Titles` | `["Custom Inventory Name"]` | Container title prefixes to skip. Colors are stripped before matching, uses starts-with logic |

### After_Scan Section

Commands executed globally after any rule confiscates or clones an item. These run in addition to per-rule `then command`/`then console` operators.

```yaml
After_Scan:
  Confiscate_Console_Commands: []
  Confiscate_Player_Commands: []
  Clone_Console_Commands: []
  Clone_Player_Commands: []
```

| Key | Description |
|-----|-------------|
| `Confiscate_Console_Commands` | Console commands after `then confiscate` or `then confiscate excess` |
| `Confiscate_Player_Commands` | Player commands after confiscation |
| `Clone_Console_Commands` | Console commands after `then clone` |
| `Clone_Player_Commands` | Player commands after clone |

#### After_Scan Variables

| Variable | Description |
|----------|-------------|
| `{player}` | Player name |
| `{date}` | Current date and time |
| `{material}` | Material name of the confiscated/cloned item |
| `{location}` | World and x-y-z coordinates |

Example: `mail send <yourName> &7[{date}] &6Confiscated {material} from {player} at {location}`

### Rules Section

Controls how rule matches are displayed and reported.

```yaml
Rules:
  Verbose: true
  Broadcast: true
  Broadcast_Format: "&8[&c{rule_name}&8] &7{item_amount}x{item_type} for &f{player}"
  Discord_Channel: none
  Discord_Format: "[{server_name}] [{location}] [{rule_name}] {item_amount}x{item_type} for {player}"
```

| Key | Default | Description |
|-----|---------|-------------|
| `Verbose` | `true` | Print `*--------- Rule match (X) for Y ---------` to console. Per-rule override: `dont verbose` |
| `Broadcast` | `true` | Send alert to players with `protect.notify.item` permission |
| `Broadcast_Format` | See above | Format for in-game broadcast |
| `Discord_Channel` | `none` | DiscordSRV channel for rule match alerts |
| `Discord_Format` | See above | Format for Discord alerts |

#### Rules Broadcast Variables

| Variable | Description |
|----------|-------------|
| `{rule_name}` | Name of the matched rule |
| `{item_amount}` | Amount of the item |
| `{item_type}` | Material name (formatted) |
| `{player}` | Player name |
| `{server_name}` | Server name |
| `{location}` | Location string |

### Other Global Settings

```yaml
Server_Name: ''
Timezone: ""
Command_Aliases: [protect, p]
Remove_Entries_Older_Than: 120 days
Register_Regions: false
Register_Tools: false
Prefix: "&8[&3Protect&8]&7"
Debug: []
Sentry: true
```

| Key | Default | Description |
|-----|---------|-------------|
| `Server_Name` | empty | Unique server identifier for proxy/remote DB networks. Must match Velocity/BungeeCord config |
| `Timezone` | empty (server default) | Timezone for `/protect logs` date filters. Example: `Europe/Budapest`, `America/New_York` |
| `Command_Aliases` | `[protect, p]` | Main command aliases |
| `Remove_Entries_Older_Than` | `120 days` | Auto-purge old database entries |
| `Register_Regions` | `false` | Enable 3D region support for `require/ignore region` operators |
| `Register_Tools` | `false` | Enable tool support (used by region wand tool, slight performance cost) |
| `Prefix` | `&8[&3Protect&8]&7` | Plugin message prefix |
| `Debug` | `[]` | Debug modes. Available: `mysql`, `scan`, `operator`. Prints detailed information to console |
| `Sentry` | `true` | Send anonymized error reports to sentry.io |

### Debug Modes

| Mode | Description |
|------|-------------|
| `mysql` | Logs database queries and connection events |
| `scan` | Logs each scan trigger, which items are checked, which items are skipped (with reason), and material/metadata checks |
| `operator` | Logs each operator evaluation, showing which conditions pass or fail for each rule |

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
