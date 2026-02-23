---
name: chests
description: 'Troubleshooting Gift, Dated, and Timed chest issues'
---

# Chest Troubleshooting

## Diagnostic Flow — "Chest not working"

1. **Ask what chest type** — Gift, Dated, or Timed?
2. **Ask what message they see** — "not ready", "already opened", "illegal break"?
3. For Dated: check current date vs sign dates and `Default_Year`

## Common Mistakes

- **Dated chest: 2 opens with preview, 1 without** — first open shows read-only preview, second open gives loot. Users report "can't take items" on first open — this is by design
- **`Default_Year` needed for year-spanning ranges** — e.g. Dec 25→Jan 3 needs `Default_Year` set to the start year (2026 for 25.12-03.01)
- **Sneaking blocks chest interaction** — players holding Shift can't open Winter chests. This prevents accidental block placement
- **`InvalidChestDateException` from corrupted sign dates** — break the sign and recreate with valid `DD.MM` format
- **Items can't be taken from preview inventory** — all clicks are cancelled in preview mode. Open the chest a second time to loot
