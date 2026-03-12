---
name: channels
description: 'Troubleshooting channel system: messaging, range, modes, proxy, and Discord linking issues'
---

# Channel Troubleshooting

## Diagnostic Flow — "Messages not showing in channel"

1. Check `Channels.Enabled: true`
2. Verify player has `chatcontrol.channel.join.{channel}.write` permission
3. Run `/channel list` to check membership
4. Enable `Rules.Verbose: true` to see if rules deny the message

## Common Mistakes

- **`Min_Players_For_Range` silently disables range** — if fewer players are within range than this threshold, range is effectively ignored. Users report "range not working" when few players are online
- **`Range_Worlds` only applies when `Range: "*"`** — the world filter is only relevant for world-wide range, not block-based range
- **`Join_Read_Old: true` auto-converts old write channel to READ** — when joining a new write channel, the previous write channel becomes READ. Users report "lost write access to old channel"
- **Console format `"none"` cancels the event** — this breaks DynMap and other plugins that listen to chat events. Use `"default"` instead if other plugins need the event
- **Manually `/channel leave`-d channels are remembered** — they won't auto-rejoin on reconnect. Users report "channel doesn't auto-join anymore" after manually leaving once
- **Proxy chat toggle** — players can `/toggle proxy_chat` to stop receiving cross-server messages while still sending to proxy channels. Requires `proxy_chat` in `Toggle.Apply_On` in settings.yml. This is the correct solution when users want to "toggle global chat" — they stay in their write channel (messages still proxy out) but incoming proxy messages are filtered
- **Discord format split** — old `Format_Discord` was replaced with `Format_To_Discord` (MC→Discord) and `Format_From_Discord` (Discord→MC)
