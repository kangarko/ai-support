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
