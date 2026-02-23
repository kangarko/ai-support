---
name: corearena-arenas
description: 'Troubleshooting arena lifecycle, phases, setup, and procedural damage issues'
---

# Arena Troubleshooting

## Diagnostic Flow — "Arena won't start / phase stuck"

1. **Ask arena state** — is it STOPPED, LOBBY, or RUNNING? (`/arena list`)
2. If won't start: check `Player_Limit.Minimum` — lobby countdown must complete with enough players
3. If phase stuck in MONSTERS mode: enable `Debug: [next-phase]` and check console

## Common Mistakes

- **Lobby point must be within the region** — the lobby location +2 blocks upward must be inside the arena region. Move lobby lower or expand region upward
- **Bees/Wolves only counted as aggressive when angry** — in MONSTERS phase mode, passive Bees/Wolves inside the region block phase advancement. Users report "phase won't advance" but the aggressive mob count isn't reaching zero
- **`Arena_End` and `Max_Phase` conflict** — if both are set, the plugin forces `Max_Phase = -1` and logs a warning. Use only one
- **Procedural Damage requires TWO enabled flags** — both `Procedural_Damage: true` in the arena file AND `Procedural_Damage.Enabled: true` in settings.yml must be set. Also requires WorldEdit. Snapshots must be taken via `/arena menu`
- **`Lifes` must be a positive integer** — if `-1` or missing, players get an error on join
