---
name: boss-skills-drops
description: 'Troubleshooting Boss skills (abilities) and drop configuration issues'
---

# Boss Skills & Drops Troubleshooting

## Diagnostic Flow — "Skill not firing / drops not working"

1. **Ask which skill** and enable `Debug: [skills]` in settings.yml
2. Check the skill delay has elapsed, Boss has a valid target, and target is within `Settings.Skills.TARGET_RANGE` (default 8 blocks)
3. Skills only fire when Boss is alive in a loaded chunk
4. For drops: enable `Debug: [commands]` and check the damage cache

## Common Mistakes

- **Arrow skill requires MC 1.11+** — uses `ProjectileHitEvent.getHitEntity()`. On older versions it returns `isCompatible() = false` and won't appear
- **`Commands` skill (non-target) silently skips `{player}`** — it has no player context. Use `Commands_Target` or `Commands_Nearby` instead. Users report "skill commands not running" — this is the #1 cause
- **`Stop_More_Skills` defaults to true** — if users want multiple skills per tick, they must set this to `false` on earlier skills. Skills are checked in registration order
- **`TaskFrozenPlayers` unfreezes all on reload** — if plugin is reloaded while players are frozen, they get unfrozen. If a player logs out frozen, they're unfrozen on next login
- **Player drops require damage within `Player_Time_Threshold`** — if no player dealt damage within this window, player-specific drops don't fire. If Boss died to environment, the system uses the damage cache to find top damagers
