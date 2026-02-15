---
name: variables
description: 'ChatControl variable and placeholder system: PlaceholderAPI expansion, custom JavaScript variables, {variable} syntax, variable files in variables/ folder, sender/receiver placeholders, PlaceholderPrefix, variable conditions. Use when working on variables/placeholders or diagnosing placeholder issues.'
---

# Variable & Placeholder System

## Overview

ChatControl provides two placeholder systems:
1. **Internal variables** — `{variable_name}` syntax used in formats, rules, messages
2. **PlaceholderAPI expansion** — `%chatcontrol_*%` for use by other plugins

Custom variables can be defined in `variables/*.yml` files with JavaScript conditions.

## Architecture

### Key Classes
- `Placeholders` (model/Placeholders.java) — PlaceholderAPI expansion class
- `PlaceholderPrefix` (core: model/PlaceholderPrefix.java) — prefix enum for sender/receiver variables
- `Variable` (Foundation: model/Variable.java) — custom variable definition
- `Variables` (Foundation: model/Variables.java) — variable replacement engine

### Variable Resolution Flow
```
Text with {variables}
  → Variables.builder() creates replacement context
    → Replace sender variables (sender_*)
    → Replace receiver variables (receiver_*)
    → Replace custom variables (from variables/*.yml)
    → Replace PlaceholderAPI %placeholders%
    → Return final text
```

## Common Issues & Solutions

### "Placeholder returns empty"
1. Database must be loaded — check `SenderCache.isDatabaseLoaded()`
2. PlaceholderAPI must be installed for `%chatcontrol_*%` variables
3. Offline players return empty (most placeholders are player-only)
4. Check variable name spelling (case-sensitive)

### "Custom variable not working"
1. Verify file is in `variables/` folder with `.yml` extension
2. Check `Key` matches what you use in formats: `{key}`
3. Ensure JavaScript `Condition` evaluates correctly
4. Use `/chc script` to test JavaScript expressions

### "Sender vs receiver variables"
- Use `{sender_*}` / `{receiver_*}` prefixes in formats
- `{player_*}` defaults to sender in most contexts
- Receiver variables only work with per-receiver component rendering

### "PlaceholderAPI from other plugins not parsed"
- ChatControl parses PAPI variables in formats and messages automatically
- Variables are replaced via Foundation's `Variables` class
- Nested PAPI variables work: `{player_prefix}` reads Vault's PAPI output

## Key File Paths

- Placeholders: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/model/Placeholders.java`
- Variable files: `chatcontrol-bukkit/src/main/resources/variables/`
- PlaceholderPrefix: `chatcontrol-core/src/main/java/org/mineacademy/chatcontrol/model/PlaceholderPrefix.java`
- Foundation Variable: `foundation-core/src/main/java/org/mineacademy/fo/model/Variable.java`
- Foundation Variables: `foundation-core/src/main/java/org/mineacademy/fo/model/Variables.java`

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
