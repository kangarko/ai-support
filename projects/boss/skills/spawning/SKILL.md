---
name: boss-spawning
description: 'Troubleshooting spawn rules, automatic spawning, and spawn condition failures'
---

# Spawn Rules Troubleshooting

## Diagnostic Flow — "Bosses not spawning from rules"

1. **Enable `Debug: [spawning]`** and check console output
2. Common blockers: no player nearby (Location_Spawn_Nearby_Player_Radius), delay not elapsed, conditions not met (wrong day/month/time/light/weather), chance roll failed, limits exceeded, chunk unloaded, Lands flag blocking
3. For REPLACE_VANILLA: check `Ignore_Replacing_Vanilla_From` in settings.yml — the spawn cause must not be ignored

## Common Mistakes

- **RESPAWN_AFTER_DEATH won't record death if Boss killed during shutdown** — the plugin must be running when the Boss dies to record the death timestamp. If the server was stopped while the Boss was alive, the rule won't know it died
- **PERIOD multiplies spawns by online player count** — each online player triggers a spawn check, so more players = more spawns. Reduce `Chance`, increase `Delay`, or tighten `Limit.Nearby_Bosses`
- **`Register_Regions` requires a server restart** when toggled — `/boss reload` is not enough
- **`Count_Unloaded_Bosses_In_Limits` only works on Paper** — on Spigot it's automatically disabled. Users on Spigot who report limit counting issues should be told this feature requires Paper

## Platform Notes

- Set `Timezone` in settings.yml for correct Days/Months conditions (e.g. `Europe/Budapest`, `America/New_York`)
