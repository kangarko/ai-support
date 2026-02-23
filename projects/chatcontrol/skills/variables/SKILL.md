---
name: variables
description: 'Troubleshooting variable/placeholder resolution, custom JavaScript variables, and PAPI integration'
---

# Variables Troubleshooting

## Common Mistakes

- **`SenderCache.isDatabaseLoaded()` prerequisite** — placeholders return empty if the database hasn't finished loading for that player. Common on join with slow databases
- **`{player_*}` defaults to sender context** — in most contexts, `{player_prefix}` = sender's prefix. Use `{receiver_prefix}` for receiver-specific values
- **Nested PAPI variables work** — `{player_prefix}` reads Vault's PAPI output. Complex nesting is supported
- **Custom variable JavaScript testable via `/chc script`** — use this to debug JavaScript conditions in `variables/*.yml` files
