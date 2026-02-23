---
name: corearena-commands
description: 'Troubleshooting /arena commands, per-arena permissions, and debug modes'
---

# Commands Troubleshooting

## Common Mistakes

- **Per-arena join permission** — `corearena.command.join.{arena}` where `{arena}` is lowercase arena name. Users often miss that each arena has its own permission
- **`/arena start` behavior depends on current state** — on STOPPED: starts lobby (no player check). On LOBBY: force-starts but still needs minimum player count. Users expect it to bypass minimum requirements
- **Debug must be YAML list format** — `Debug: [arena, next-phase]`, not `Debug: arena`. A plain string silently fails
