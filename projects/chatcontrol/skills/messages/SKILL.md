---
name: messages
description: 'ChatControl message broadcasting: join/quit/kick/death/timed messages, .rs message files, conditions (require/ignore sender/receiver), message groups, formats, random/sequential messages, proxy broadcasting. Use when configuring join/quit/death/timed messages or diagnosing broadcast issues.'
---

# Message Broadcasting System

## Overview

ChatControl replaces vanilla join/quit/kick/death messages and adds scheduled timed broadcasts. Messages are defined in `.rs` files under `messages/` with conditional logic, formatting, and proxy support.

## Architecture

### Key Classes
- `PlayerMessage` (operator/PlayerMessage.java) — abstract base for all message types
- `PlayerMessages` (operator/PlayerMessages.java) — singleton loader and broadcaster
- `JoinQuitKickMessage` (operator/JoinQuitKickMessage.java) — wrapper for join/quit/kick
- `DeathMessage` (operator/DeathMessage.java) — death-specific conditions (killer, cause, etc.)
- `TimedMessage` (operator/TimedMessage.java) — scheduled broadcast with delay
- `PlayerMessageType` (core: model/PlayerMessageType.java) — enum: JOIN, QUIT, KICK, DEATH, TIMED

### Broadcast Flow
```
Event triggers (join/quit/death/timer)
  → PlayerMessages.broadcast(type, wrapped, message)
    → For each message group (top to bottom):
      1. Check sender conditions (require/ignore sender perm/script/world/etc.)
      2. Check timing (begins/expires/delay)
      3. Select message text (random or sequential)
      4. Build format using Format.parse()
      5. For each receiver: check receiver conditions
      6. Send formatted component
      7. Fire PlayerMessageEvent (API)
      8. If Settings.Messages.STOP_ON_FIRST_MATCH: stop after first match
```

## Common Issues & Solutions

### "Join/quit messages not showing"
1. Check `Messages.Apply_On` contains `join`/`quit`
2. Verify no other plugin cancels the event
3. Check `Stop_On_First_Match` — first match stops all further groups
4. Ensure message group order: most specific on top

### "First-join detection not working"
- Use `require sender script {statistic_PLAY_ONE_MINUTE} == 0`
- MC 1.13+: `PLAY_ONE_MINUTE` (misleading name — counts in ticks)
- MC 1.7-1.12: `PLAY_ONE_TICK`
- Place first-join group ABOVE default join (Stop_On_First_Match)

### "Death message shows wrong format"
1. Check `require cause` matches the death type
2. Entity names changed in MC 1.20.5+ (LIGHTNING_BOLT, TNT, END_CRYSTAL)
3. Killer item supports wildcards (`*_SWORD`, `DIAMOND_*`)
4. `{killer}` is null for environmental deaths — check for it

### "Timed messages not cycling"
- Default is sequential (not random). Use `random true` for random.
- `delay` per-group overrides global `Timed_Delay`
- Timed messages skip first run after reload (prevents spam)
- Timer resets on `/chc reload`

### "Message shows to wrong players"
- Use `require receiver world/perm/script` to filter recipients
- `require self` / `ignore self` controls self-visibility
- Channel conditions restrict to channel members

## Key File Paths

- PlayerMessage: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/operator/PlayerMessage.java`
- PlayerMessages: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/operator/PlayerMessages.java`
- DeathMessage: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/operator/DeathMessage.java`
- TimedMessage: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/operator/TimedMessage.java`
- Message files: `chatcontrol-bukkit/src/main/resources/messages/`
- Settings: `chatcontrol-bukkit/src/main/resources/settings.yml` (Messages section)

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
