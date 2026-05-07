---
name: channels
description: 'Troubleshooting channel system: messaging, range, modes, proxy, and Discord linking issues'
---

# Channel Troubleshooting

## Vocabulary — User phrasing → ChatControl primitives

When a user describes what they want using non-plugin terms, translate FIRST, then search. Most "this feature doesn't exist" mistakes come from taking the user's words literally instead of mapping them to what ChatControl actually ships.

- "send one message without joining" / "broadcast to a channel I'm not in"
  → `/channel send <channel> <message>` — see `command/channel/SendChannelSubCommand.java`.
- "send as another player" / "post on someone's behalf"
  → `/channel send-as <player> <channel> <message>` — see `command/channel/SendAsChannelSubCommand.java`.
- "monitor channel without joining" / "listen in" / "moderator view"
  → `/spy toggle chat <channel>` — see `command/CommandSpy.java` and the `Spy` class. Requires `chatcontrol.command.spy` plus `chatcontrol.spy.type.chat`.
- "auto-switch channel by region/area/world"
  → No native region listener. Per-world: write a rule with `#require world <name>`. Per-region: external region plugin (WorldGuard region-events, Residence flags, Lands enter handler) running `/channel join <name>` from console.
- "auto-join on connect" / "auto-join when joining server"
  → `Channels.List.<name>.Auto_Join` permission-based group config in `settings.yml`. Once a player manually `/channel leave`s, that channel is remembered as left (see Common Mistakes below) and will not auto-rejoin.
- "private chat" / "team chat" / "guild chat"
  → A channel with `Range: party` or `Party: <provider>` (Towny, Factions, Lands, mcMMO, SimpleClans, Parties). For 2-player private DMs use the `/tell` system, not channels.
- "filter / block / replace words in chat"
  → Rules engine (`chatcontrol-bukkit/src/main/resources/rules/chat.rs`), not channels.
- "alias /h to /helpop" / "rename a command" / "create a command"
  → Default rules in `command.rs` already map `/helpop`, `/nick`, `/help`, `/ping` etc. as a pattern. Add a new `#match ^[/]<alias>` block and `#then command <real command> $1`.

If a translation isn't listed here and you're tempted to refuse, follow the prove-the-gap rule: cite the rule files and command directory you searched, and which terms you grep'd, BEFORE saying it doesn't exist.

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
