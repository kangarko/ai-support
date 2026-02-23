---
name: worldedit-config
description: 'Troubleshooting WorldEdit limits, global ignore settings, and after-scan hooks'
---

# WorldEdit & Config Troubleshooting

## Common Mistakes

- **`protect.group.{group}` confusion with rule groups** — two unrelated "group" concepts. WorldEdit groups = permission-based block limits. Rule groups = reusable operator sets in `group.rs`. Major user confusion source
- **`Ignore.Worlds` validates world names on load** — if a listed world isn't loaded when Protect starts, you get errors. Ensure Protect loads AFTER world management plugins (Multiverse, etc.)
- **`After_Scan` only fires for confiscate/clone actions** — not for `then command`. Users report "After_Scan commands not running" for rules that only use `then command` — those run directly from the rule, not via After_Scan
- **Broadcast deduplication per scan** — `ProtectCheck` tracks already-sent notify messages per scan to prevent duplicates. If seeing duplicates, multiple scans may be triggering simultaneously (e.g. join + inventory open)
