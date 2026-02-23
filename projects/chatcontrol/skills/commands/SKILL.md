---
name: commands
description: 'Troubleshooting ChatControl commands, aliases, and conflict resolution'
---

# Commands Troubleshooting

## Common Mistakes

- **Use namespaced commands for conflicts** — `/chatcontrol:tell` bypasses other plugins' `/tell` commands
- **Reply requires recent PM exchange** — `PlayerCache.replyPlayerName` must be set from a previous message. No prior PM = no reply target
- **Tab completion bypass permission** — `chatcontrol.bypass.tab.complete` may interfere with expected tab behavior
