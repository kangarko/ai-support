---
name: tags-nicks
description: 'Troubleshooting tag/nick display, validation, persistence, and character limits'
---

# Tags & Nicks Troubleshooting

## Common Mistakes

- **Tab/nametag has 16 char limit** — Minecraft protocol limitation. Color codes count toward the limit. `&c&lVIP` = 6 chars used for formatting alone
- **Tag rules validated via `rules/tag.rs`** — "Tag is not allowed" errors come from rule matching. Check tag rules for blocking patterns
- **Tag lost on rejoin = database issue** — tags persist via database. Check `database.yml` connection and look for database errors in console on join
- **Color codes count toward the 16 char limit in tab/nametag** — users set colored tags that look fine in chat but get truncated in tab. This is NOT a bug, it's a Minecraft protocol limit
