---
name: chat-filter
description: 'ChatControl built-in chat filters: anti-spam, anti-caps, anti-bot, parrot detection, similarity checking, message delay, grammar correction, newcomer restrictions, unicode filtering. Use when diagnosing spam protection, caps issues, bot detection, or message rate limiting.'
---

# Chat Filter System

## Overview

The built-in chat filter (Checker) runs BEFORE the rules engine. It handles anti-spam, anti-caps, anti-bot, parrot detection, similarity checking, and grammar corrections. Configured in `settings.yml` under `Anti_Spam`, `Anti_Caps`, `Anti_Bot`, and `Newcomer` sections.

## Architecture

### Key Classes
- `Checker` (model/Checker.java) — main filter entry point
- `Newcomer` (model/Newcomer.java) — newcomer restriction logic
- `WarningPoints` (model/WarningPoints.java) — warning point tracking and thresholds

### Filter Pipeline (order matters)
```
Message received
  → Anti-Bot checks (moved? cooldown expired?)
    → Newcomer restrictions (playtime threshold checks)
      → Anti-Spam delay check (time between messages)
        → Anti-Spam period limit (max messages in time window)
          → Similarity check (compared to past messages)
            → Parrot detection (copying other players)
              → Anti-Caps processing
                → Grammar corrections (capitalize, period)
                  → Rules engine (separate system)
```

## Common Issues & Solutions

### "Messages blocked but player isn't spamming"
1. Check `Similarity` threshold — may be too low (80% is usually good)
2. Check `Similarity_Past_Messages` — compare against fewer messages
3. Add pattern to `Whitelist_Similarity` if it's a false positive
4. `Similarity_Start_At` > 1 allows first few duplicates through

### "Parrot detection false positives"
- Add common phrases to `Parrot.Whitelist` (greetings like "hi", "gg")
- Increase `Parrot.Similarity` threshold
- Decrease `Parrot.Delay` window

### "Anti-caps breaks abbreviations"
- Add abbreviations to `Anti_Caps.Whitelist` (e.g., `PVP`, `OMG`)
- Increase `Min_Caps_In_A_Row` for less aggressive detection

### "Newcomer threshold wrong"
- Uses `PLAY_ONE_MINUTE` statistic (actually measures ticks, not minutes)
- Requires world stats file: `world/stats/<uuid>.json`
- Does NOT count time on other servers in a proxy network

### "Warning points not accumulating"
- Enable `Warning_Points.Enabled: true`
- Verify trigger formulas are valid JavaScript
- Check set names match between `Sets` and rule `then points` calls
- Points reset on reload (stored in memory)

## Key File Paths

- Checker class: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/model/Checker.java`
- Newcomer: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/model/Newcomer.java`
- Warning points: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/model/WarningPoints.java`
- Settings: `chatcontrol-bukkit/src/main/resources/settings.yml` (Anti_Spam, Anti_Caps, Anti_Bot, Newcomer, Warning_Points)

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
