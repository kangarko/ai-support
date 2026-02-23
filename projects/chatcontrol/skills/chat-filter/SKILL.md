---
name: chat-filter
description: 'Troubleshooting built-in chat filters: anti-spam, anti-caps, anti-bot, parrot detection, similarity checking, newcomer restrictions. Use when diagnosing filter bypass, false positives, or message blocking issues.'
---

# Chat Filter Troubleshooting

## Diagnostic Flow — "Filter bypass permission not working"

1. **FIRST: Ask what exact message the user sees** — is it a chat message, title, actionbar, or bossbar?
2. **Compare against ChatControl's known messages** — ChatControl's filter messages come from `en_US.json` and are sent as chat messages:
   - Anti-caps: `"Please avoid excessive capitalization in your {type}."`
   - Anti-spam delay: `"Please wait {time} before typing again."`
   - Similarity: `"Avoid sending similar messages repeatedly."`
3. **If the message text or format doesn't match ChatControl's** → it's from another plugin. Common culprits:
   - **CMI** — has its own anti-caps filter that shows "Too many caps" as a **title message**
   - **Vulcan** — anticheat with chat rate limiting
   - **LiteBans** — has mute messages that look like filter blocks
4. **Ask for `/plugins` output** if another plugin is suspected
5. Only after confirming the message IS from ChatControl, proceed to permission debugging

## Common Mistakes

- **`PLAY_ONE_MINUTE` statistic actually measures TICKS, not minutes** — newcomer threshold calculations must account for this (20 ticks = 1 second, 1200 ticks = 1 minute)
- **Newcomer playtime doesn't count cross-server proxy time** — only tracks time on the current server via world stats file `world/stats/<uuid>.json`
- **`Similarity_Start_At > 1` allows first N duplicate messages through** — users report "similarity check doesn't catch the first copy" — this is intentional
- **Warning points are stored in memory only** — they reset on plugin reload. Users report "points disappeared after reload"
- **Parrot detection false positives** — add common greetings ("hi", "gg", "gg wp") to `Parrot.Whitelist`

## Anti-Caps Quick Reference

- Bypass permission: `chatcontrol.bypass.caps`
- Warning message: `"Please avoid excessive capitalization in your {type}."` (chat message, NOT title/actionbar)
- Whitelist common abbreviations in `Anti_Caps.Whitelist` (e.g. `PVP`, `OMG`, `LOL`)
- Increase `Min_Caps_In_A_Row` for less aggressive detection

## Cross-Plugin Conflicts

- **CMI** has its own anti-caps filter → shows "Too many caps" as a TITLE. If user reports caps bypass not working and sees a title message, it's CMI, not ChatControl
- Disable CMI's caps filter in CMI's config to avoid double-filtering
