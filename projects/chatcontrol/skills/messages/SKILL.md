---
name: messages
description: 'Troubleshooting join/quit/kick/death/timed messages and broadcast conditions'
---

# Messages Troubleshooting

## Common Mistakes

- **First-join detection trick: `{statistic_PLAY_ONE_MINUTE} == 0`** — misleading statistic name. It actually counts TICKS played, not minutes. Value 0 = never played before
- **Entity names changed in MC 1.20.5+** — `LIGHTNING_BOLT`, `TNT`, `END_CRYSTAL` (was `LIGHTNING`, `PRIMED_TNT`, `ENDER_CRYSTAL`). Death message `require cause` patterns must match the current MC version's names
- **`{killer}` is null for environmental deaths** — use `require killer` condition to guard against null. Commands with `{killer}` silently skip when null
- **`Stop_On_First_Match` ordering matters** — first matching message group stops all further groups. Place most specific groups (first-join, VIP) ABOVE default groups
