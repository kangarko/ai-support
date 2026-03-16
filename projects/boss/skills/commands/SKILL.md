---
name: boss-commands-permissions
description: 'Troubleshooting Boss commands, PAPI placeholders, and permission issues'
---

# Boss Commands & Permissions Troubleshooting

## Diagnostic Flow — "Command / placeholder not working"

1. **Ask what exact command or placeholder** they're using and what output they see
2. For commands: check permission with `/boss perms`. OPs have all permissions by default
3. For PAPI: check `/papi list` shows `boss` expansion
4. If PAPI returns empty: is it being called async? (see CMI conflict below)

## Common Mistakes

- **PAPI placeholders return empty when called async** — CMI and some plugins call placeholders from async threads. The nearest-Boss placeholders (`%boss_name%`, health, location, top damage) require the main thread. If called async, they return empty and log a warning. Tell the user to contact the calling plugin's developers
- **`%boss_name%` always empty** — player must have recently damaged a Boss within `Variables.Nearby_Boss_Radius` blocks (default 20). Increase this in settings.yml
- **Health bar only shows on player→Boss damage**, not when Boss damages the player. Users report "health bar not appearing" — confirm they're hitting the Boss, not being hit
- **`/boss scan` is console-only** — won't run from in-game. Also requires running twice for safety confirmation
- **`~` relative coordinates only work for in-game players**, not console. Console must use absolute world/x/y/z values

## Boss Death Command Variables

These variables are replaced in all Boss commands (death, skill, etc.):

| Variable | Value |
|---|---|
| `{boss_name}` | Boss config name |
| `{boss_alias}` | Boss display alias |
| `{boss_world}` | World name where boss died |
| `{boss_x}` | Boss block X coordinate |
| `{boss_y}` | Boss block Y coordinate |
| `{boss_z}` | Boss block Z coordinate |
| `{boss_location}` | Full serialized location |
| `{player}` / `{killer}` | Killer player name (empty if no player) |

**Deprecated aliases** (still work): `{boss}`, `{alias}`, `{world}`, `{x}`, `{y}`, `{z}`

### Console Commands & `execute positioned`

When a Boss dies without a player killer (e.g. Wither effect, fall, environment), death commands run as console. Console has no position context, so `~ ~ ~` relative coordinates fail.

To run a summon/particle/etc at the boss's death location from console, use:
```yaml
execute positioned {boss_x} {boss_y} {boss_z} run summon silverfish ~0.5 ~ ~0.5
```

Common mistake: writing `execute positioned run summon ...` without coordinates causes `CommandSyntaxException: Expected double`. The `positioned` subcommand always requires explicit `<x y z>` coordinates.

### Commands with `{player}` or `{killer}`

If the command contains `{player}` or `{killer}` and no player killed the Boss, the command is **silently skipped** (not executed at all). Use `{boss_x}/{boss_y}/{boss_z}` for position-dependent commands that must always run.
