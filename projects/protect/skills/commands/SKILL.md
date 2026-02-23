---
name: commands
description: 'Troubleshooting Protect commands, permissions, and common permission confusion'
---

# Commands & Permissions Troubleshooting

## Common Mistakes

- **`protect.bypass.scan` is explicitly FALSE for OPs** — unlike most permissions, OP status does NOT grant this. Must be granted via a permissions plugin. Alternatively set `Ignore.Ops: true` in settings.yml
- **`/protect edititem amount ≥384` triggers warning** — because the default `over-64` rule will confiscate items with 65+ stacks, and `unnatural-stack` catches anything over the natural max
- **`protect.group.{group}` is for WorldEdit limits, NOT rule groups** — two unrelated "group" concepts exist. WorldEdit groups use `protect.group.{name}` permission mapped to `WorldEdit.Total_Limit` config. Rule groups use `ignore perm` operators for bypass. Major confusion source
- **Playtime requires `spigot.yml` `stats.disable-saving: false`** — if stats saving is disabled, playtime tracking is unavailable and `require/ignore playtime` operators will throw an error
