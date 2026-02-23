---
name: corearena-signs-setup
description: 'Troubleshooting arena signs, setup tools, WorldEdit restore, and MySQL sync'
---

# Signs & Setup Troubleshooting

## Common Mistakes

- **Power sign crash = permanent redstone block** — the power sign converts to a redstone block for 5 ticks then back. If the server crashes during those 5 ticks, the block stays as redstone permanently. Must manually replace with a sign and recreate
- **`[classes]` and `[rewards]` are unregistered shortcut signs** — they open menus but are NOT in the SignType enum. Users looking at the sign type list won't find them
- **MySQL `Delay_Ticks` formula**: `(roundtrip_ms / 50) + 6` — users with high-latency MySQL need to increase this value. Use `Debug: [mysql]` and check "took y ms" logs
- **WorldEdit restore can cause lag** — lower `Block_Bulk_Restore_Amount` and/or increase `Wait_Period`. Ensure lobby duration is long enough for the arena to finish restoring
