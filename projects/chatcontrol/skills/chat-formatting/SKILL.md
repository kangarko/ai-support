---
name: chat-formatting
description: 'ChatControl format system: format files, parts, placeholders, hover/click events, gradients, images, MiniMessage, colors, decorations. Use when working on format code, diagnosing format issues, or configuring chat appearance.'
---

# Chat Formatting System

## Overview

Formats define how messages appear in chat. Each format is a YAML file in `formats/` containing ordered "parts" — conditional sections with text, hover events, click actions, and images. Formats support MiniMessage, legacy `&` colors, gradients, and JavaScript conditions.

## Architecture

### Key Classes
- `Format` (model/Format.java) — loads from `formats/*.yml`, builds `SimpleComponent` via `Format.build()`
- `Format.Part` — one section of a format with message, conditions, hover/click
- `Colors` (model/Colors.java) — manages color permissions and application
- `TagResolverColorsForPerm` — resolves which MiniMessage tags a player can use based on permissions
- `SimpleComponent` (Foundation) — the component builder that assembles the final output

### Format Resolution Flow
```
Channel/Command specifies Format name
  → Format.parse(name) loads formats/{name}.yml (or creates literal format)
    → For each Part (top to bottom):
      1. Check Sender_Permission / Sender_Condition / Sender_Variable
      2. Replace variables in Message text
      3. Apply Hover / Click / Image
      4. Set Receiver_Permission / Receiver_Condition / Receiver_Variable (view conditions)
    → Append all passing parts into SimpleComponent
  → Return final component
```

## Common Issues & Solutions

### "Format part not showing"
1. Check sender has required permission (`Sender_Permission`)
2. Check receiver has required permission (`Receiver_Permission`)
3. Test JavaScript conditions with `/chc script` command
4. Verify variable syntax: `{player_prefix+}` vs `{player_prefix}`

### "Colors not working"
1. Verify `Colors.Apply_On` contains the context (e.g., `chat`)
2. Check player has `chatcontrol.color.{name}` permission
3. Rules may strip colors — look for `then replace` operators in rules
4. Hex colors require explicit `chatcontrol.hexcolor.*` permission

### "Gradient breaks with inner colors"
Gradients are "unsafe" — MiniMessage tags inside `Message` break the gradient rendering. Use gradients only on plain text without inner color tags.

### "Run_Command only works once"
Minecraft limitation: only ONE `Run_Command` per part. Split into separate parts if multiple commands needed.

### "Hover not showing on old versions"
Pre-1.13: max 21 characters per hover line. Use shorter text.

## Key File Paths

- Format files: `chatcontrol-bukkit/src/main/resources/formats/`
- Format class: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/model/Format.java`
- Colors class: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/model/Colors.java`
- Settings: `chatcontrol-bukkit/src/main/resources/settings.yml` (Colors section)

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
