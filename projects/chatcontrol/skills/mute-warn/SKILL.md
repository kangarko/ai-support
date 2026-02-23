---
name: mute-warn
description: 'Troubleshooting mute hierarchy, warning points, duration format, and point decay'
---

# Mute & Warning Troubleshooting

## Diagnostic Flow — "Player can still chat while muted"

1. Check mute is active and hasn't expired
2. Check `Mute.Prevent_Writing: true`
3. Check `Soft_Mute` setting — if true, the muted player sees their own messages (thinks they're chatting normally but nobody else sees them)
4. Channel mute only affects that channel — player may chat in other channels
5. Check `chatcontrol.bypass.mute` permission

## Common Mistakes

- **`Soft_Mute` is deceptive by design** — muted player sees their own messages and thinks they're chatting normally. Other players don't see anything. Users (admins) report "mute isn't working" because the muted player doesn't complain — they don't know they're muted
- **Duration format is strict: `30m` not `30 m`** — no spaces between number and suffix. `s`/`m`/`h`/`d` suffixes. No duration = permanent
- **Point decay only for online players** — offline players retain their points indefinitely. Points only decay via the `Reset_Task` when the player is online
- **Mute hierarchy: proxy > server > channel > player** — higher-level mutes take priority

## Cross-Plugin Conflicts

- Mute state is checked in the channel send pipeline. If another plugin handles chat before ChatControl, the mute may not apply
