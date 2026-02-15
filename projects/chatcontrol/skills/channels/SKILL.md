---
name: channels
description: 'ChatControl channel system: channel creation, types, ranged channels, party channels, permissions, auto-join, channel modes (read/write), proxy channels, Discord linking. Use when working on channel code or diagnosing channel-related issues.'
---

# Channel System

## Overview

Channels route chat messages to specific groups of players. Each channel has a format, optional range limit, party integration, proxy support, and Discord linking. Players join channels in READ (receive-only) or WRITE (send+receive) mode. Only one WRITE channel at a time.

## Architecture

### Key Classes
- `Channel` (model/Channel.java) — extends `YamlConfig`, loaded from `settings.yml` `Channels.List`
- `Channel.State` — encapsulates message state (sender, message, component, variables)
- `ChannelMode` (core: model/ChannelMode.java) — enum: `WRITE` (gold), `READ` (green)
- `ChannelCommands` (command/channel/) — `/channel` subcommands
- `ChatHandler` (listener/chat/) — routes chat to channels

### Message Send Pipeline
```
Player types message
  → ChatHandler routes to write channel
    → Channel.sendMessage(State)
      1. Compile receivers (range, party, vanish, ignore checks)
      2. Fire ChannelPreChatEvent (API — cancellable)
      3. Check mute status (player, channel, server, proxy)
      4. Remove unauthorized colors
      5. Run rules/filters via Checker.filterChannel()
      6. Process @mentions and sound notifications
      7. Format.build() — compile format parts into component
      8. Send to each receiver (with per-receiver view conditions)
      9. Log to console and database
      10. Forward to Discord (if Discord_Channel_Id set)
      11. Forward over proxy (if Proxy: true)
      12. Fire ChannelPostChatEvent
```

## Common Issues & Solutions

### "Messages not showing in channel"
1. Check `Channels.Enabled: true` in settings.yml
2. Verify player has `chatcontrol.channel.join.{channel}.write`
3. Run `/channel list` to check membership
4. Check `Ignore_Worlds` doesn't include current world
5. Enable `Rules.Verbose: true` to see if rules deny the message

### "Ranged channel not working"
1. Check `Range` value is a number (blocks) or `*` (world-wide)
2. `Min_Players_For_Range` may prevent range from activating
3. `Range_Worlds` only applies when `Range: "*"`
4. `chatcontrol.bypass.range` reaches everyone — check staff perms
5. Party option may override range behavior

### "Player can't leave/switch channels"
- Players can only be in ONE write channel. Joining a new write channel leaves the old one.
- `Join_Read_Old: true` auto-converts old write channel to READ mode
- Manually left channels (`/channel leave`) are remembered — won't auto-rejoin

### "Console format shows wrong output"
- `"none"` cancels the event (bad for DynMap, other plugins)
- `"default"` uses the channel's formatted output as-is

### "Discord messages showing wrong format"
- Old `Format_Discord` was split: use `Format_To_Discord` (MC→Discord) and `Format_From_Discord` (Discord→MC)

## Key File Paths

- Channel class: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/model/Channel.java`
- Channel mode: `chatcontrol-core/src/main/java/org/mineacademy/chatcontrol/model/ChannelMode.java`
- Channel commands: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/command/channel/`
- Chat handler: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/listener/chat/ChatHandler.java`
- Settings: `chatcontrol-bukkit/src/main/resources/settings.yml` (Channels section)

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
