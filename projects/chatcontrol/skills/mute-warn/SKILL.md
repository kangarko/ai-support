---
name: mute-warn
description: 'ChatControl mute and warn system: /mute, /unmute, temp mute, channel mute, server mute, proxy mute, warning points, point sets, point triggers, punishment escalation, point decay. Use when diagnosing mute behavior, warning points, punishments, or mute hierarchy issues.'
---

# Mute & Warning System

## Overview

ChatControl provides a hierarchical mute system (player, channel, server, proxy) and a warning points system with configurable thresholds, triggers, and decay. Mutes and warns integrate with rules, spy, and proxy sync.

## Mute Architecture

### Mute Hierarchy (highest to lowest priority)
```
Proxy mute (all servers)
  ↓
Server mute (all channels on one server)
  ↓
Channel mute (one channel)
  ↓
Player mute (one player)
```

### Key Classes
- `Mute` (model/Mute.java) — mute state management
- `CommandMute` (command/CommandMute.java) — `/mute` command
- `CommandUnmute` (command/CommandUnmute.java) — `/unmute` command
- `PlayerCache` — stores mute state per player

### Mute Types
| Scope | Description | Storage |
|-------|-------------|---------|
| Player mute | Individual player can't chat | `PlayerCache.muteData` |
| Channel mute | Entire channel silenced | `Channel.mutedUntil` |
| Server mute | All chat silenced | Global flag |
| Proxy mute | All servers silenced | Proxy broadcast |

### Mute Data Structure
```java
class MuteData {
    UUID mutedBy;           // Who muted
    long mutedUntil;        // Expiration timestamp (-1 = permanent)
    String reason;          // Mute reason
    MuteType type;          // PLAYER, CHANNEL, SERVER, PROXY
    String channelName;     // For channel mutes
    boolean anonymous;      // Hide muter identity
}
```

## Common Issues & Solutions

### "Muted player can still chat"
1. Check mute is active: `/chc points <player>` or check logs
2. Check `Mute.Prevent_Writing: true`
3. Check `Mute.Soft_Mute` — if true, they see own messages
4. Channel mute only affects that channel; player may chat elsewhere
5. Check `chatcontrol.bypass.mute` permission — bypasses mute

### "Mute expires immediately"
- Duration format: `30s`, `5m`, `2h`, `1d` (s/m/h/d suffixes)
- No spaces: `30m` not `30 m`
- No duration = permanent (`-1` timestamp)

### "Warning points not accumulating"
1. Check `Warning_Points.Enabled: true`
2. Check rule uses `warn <setname>` operator
3. Set name must match a `Sets.<name>` in config
4. Check rule actually matches (test with `/chc rule test <message>`)

### "Trigger action not firing"
1. Check `Trigger_Amount` threshold reached
2. Check action syntax (console/player/warn/kick)
3. Check `Reset_Points: true/false` — if true, points reset after trigger
4. Check command exists and works manually

### "Proxy mute not syncing"
1. Proxy plugin must be installed on BungeeCord/Velocity
2. `proxy.yml` configured with same `Server_Name`
3. Mute must be `proxy` scope (not just server/channel)
4. SyncType.MUTE must be enabled in proxy config

### "Points not decaying"
1. Check `Reset_Task.Enabled: true`
2. Check `Reset_Task.Period` isn't too long
3. Player must be online for decay (offline players retain points)

## Key File Paths

- Mute: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/model/Mute.java`
- CommandMute: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/command/CommandMute.java`
- CommandUnmute: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/command/CommandUnmute.java`
- Warning Points config: `chatcontrol-bukkit/src/main/resources/settings.yml` (Warning_Points section)
- Rule operators: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/operator/RuleOperator.java`

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
