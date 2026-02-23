---
name: boss-creation
description: 'Troubleshooting Boss creation, spawning failures, equipment, attributes, and model issues'
---

# Boss Troubleshooting

## Diagnostic Flow — "Boss won't spawn / looks wrong"

1. **Ask what happens** — does the Boss not appear at all, or does it appear with wrong properties?
2. If not appearing: ask for `/boss list` output and check `Debug: [spawning]` console output
3. If wrong health: check `spigot.yml` → `settings.attribute.maxHealth.max` — Boss health MUST NOT exceed this value
4. If equipment missing: what entity type? Only Monsters, Players, Horses, and ArmorStands can wear equipment. Horses use only the CHEST slot (for horse armor)
5. If model missing: does their ModelEngine model ID match exactly? Invalid models are auto-removed with a console warning

## Common Mistakes

- **Commands with `{player}` silently skip** when no player killer exists (e.g. Boss died to environment). Users report "commands not running" — check if the Boss died to a mob or fall damage. Use `Commands_Target` instead of `Commands` for player-specific commands
- **Riding Boss names are case-sensitive** — must exactly match the Boss file name. A Boss cannot ride itself (infinite loop protection exists)
- **Attributes are entity-type-specific** — incompatible attributes are silently skipped. The GUI menu shows which attributes are available for each type
- **Custom settings are entity-type-specific** — e.g. `Baby` only works on Zombies and Ageable entities. `canApplyTo()` checks compatibility silently

## Cross-Plugin Conflicts

- **Citizens NPC Bosses** require Citizens plugin installed + `Citizens.Enabled: true` + target/wander goals configured. The Boss entity type must support NPC pathfinding
