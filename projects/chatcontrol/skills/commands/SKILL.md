---
name: commands
description: 'ChatControl command system: /chc subcommands, /channel, /tell, /reply, /ignore, /mail, /mute, /spy, /tag, /toggle, /me, /say, /motd, /list, /realname, permissions, tab completion. Use when working on command code, diagnosing command issues, or looking up command syntax.'
---

# Command System

## Overview

ChatControl registers a main `/chc` (ChatControl) command group with many subcommands, plus standalone commands like `/tell`, `/channel`, `/mail`, etc. All command aliases are configurable in `settings.yml`.

## Architecture

### Key Classes
- `ChatControlCommands` (command/chatcontrol/) — main `/chc` command group
- `ChannelCommands` (command/channel/) — `/channel` command group
- `SharedChatControlCommandCore` — shared helper interface with lookup utilities
- Various `Command*.java` files — standalone commands

### Foundation Command Framework
- `SimpleCommandGroup` — groups subcommands under one label
- `SimpleCommand` / `SimpleSubCommand` — individual command implementations
- `@Permission` / `@PermissionGroup` annotations — permission declarations

## Common Issues & Solutions

### "Command not found"
1. Check command aliases in settings.yml
2. Verify player has the permission node
3. `/chc perms` lists all available permissions
4. Other plugins may override command aliases

### "Tab completion not working"
1. ChatControl uses Foundation's tab completion system
2. Check `tabComplete()` method in the command class
3. Verify `chatcontrol.bypass.tab.complete` isn't interfering

### "Can't tell/reply to offline player"
- PMs require target to be online (or on proxy network)
- Reply requires recent PM exchange (`PlayerCache.replyPlayerName`)

### "Command conflicts with other plugins"
- Change aliases in settings.yml to avoid conflicts
- ChatControl registers commands at plugin load
- Use namespaced commands: `/chatcontrol:tell`

## Key File Paths

- Main command group: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/command/chatcontrol/`
- Channel commands: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/command/channel/`
- Standalone commands: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/command/`
- Shared utilities: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/command/SharedChatControlCommandCore.java`
- Permissions: `chatcontrol-core/src/main/java/org/mineacademy/chatcontrol/model/Permissions.java`

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
