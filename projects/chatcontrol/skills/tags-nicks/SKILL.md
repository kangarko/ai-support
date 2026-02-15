---
name: tags-nicks
description: 'ChatControl tags and nicks: player prefix, suffix, nick, /tag command, vault integration, tag rules, tag colors, tag formatting, permission-based tags, nick validation. Use when diagnosing tag display, nick setting, or player name customization issues.'
---

# Tags & Nicks

## Overview

ChatControl allows players to set custom tags (prefix, nick, suffix) that display in chat, tab list, and above head. Tags can be color-formatted with permission-based restrictions and rule validation.

## Architecture

### Key Classes
- `Tag` (model/Tag.java) — tag management logic
- `TagType` — enum: `PREFIX`, `NICK`, `SUFFIX`
- `CommandTag` (command/CommandTag.java) — `/tag` command
- `PlayerCache` — stores tag data: `playerTag` / `playerNick` / `playerSuffix`

### Tag Types
| Type | Description | Display Position |
|------|-------------|-----------------|
| `PREFIX` | Text before name | `[PREFIX] Name` |
| `NICK` | Custom display name | Replaces actual name |
| `SUFFIX` | Text after name | `Name [SUFFIX]` |

### Tag Flow
```
/tag <type> <value>
  → CommandTag validates args
    → Tag.setTag(sender, type, value)
      1. Check permission (chatcontrol.command.tag.<type>)
      2. Strip unauthorized colors
      3. Validate against tag rules (rules/tag.rs)
      4. Check min/max length
      5. Check banned words/patterns
      6. Store in PlayerCache
      7. Update display (chat format, tab, nametag)
      8. Save to database
```

## Common Issues & Solutions

### "Tag not showing in chat"
1. Check `Tag.Enabled: true`
2. Check `Tag.Apply_On.Chat: true`
3. Format file must use `{player_tag_prefix}` / `{player_tag_nick}` / `{player_tag_suffix}` variables
4. Check format condition isn't hiding empty tags incorrectly

### "Tag colors not working"
1. Player needs `chatcontrol.tag.color.<color>` permission
2. `&` codes must match server's color system
3. Hex colors need `chatcontrol.tag.color.hex` permission
4. Gradients need `chatcontrol.tag.color.gradient` permission

### "'Tag is not allowed' error"
1. Check `rules/tag.rs` for blocking rules
2. Check min/max length limits
3. Tag may contain banned word matching a rule pattern
4. Special characters may be blocked by rules

### "Nick not replacing name in tab/nametag"
1. Check `Tag.Apply_On.Tab: true` for tab list
2. Check `Tag.Apply_On.Nametag: true` for above-head
3. Tab/nametag has 16 char limit (Minecraft protocol)
4. Color codes count toward character limit in tab/nametag

### "Tag lost on rejoin"
1. Check database is configured and working
2. Tag should persist via PlayerCache → database save
3. Check database.yml connection settings
4. Look for database errors in console on join

### "Tag breaks chat format alignment"
- Tags with variable lengths cause alignment issues in fixed-width formats
- Use condition parts to hide empty tags
- Consider padding or consistent tag lengths

## Key File Paths

- Tag: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/model/Tag.java`
- CommandTag: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/command/CommandTag.java`
- Tag rules: `chatcontrol-bukkit/src/main/resources/rules/tag.rs`
- Settings: `chatcontrol-bukkit/src/main/resources/settings.yml` (Tag section)
- Player data: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/model/db/PlayerCache.java`

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
