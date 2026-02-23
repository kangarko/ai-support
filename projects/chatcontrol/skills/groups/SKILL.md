---
name: groups
description: 'Troubleshooting ChatControl permission groups and setting overrides'
---

# Permission Groups Troubleshooting

## Critical Concept — TWO Unrelated "Group" Meanings

This is the **#1 confusion source** across all ChatControl support:

1. **PlayerGroup** (settings.yml `Groups`) — permission-based setting overrides. Uses `chatcontrol.group.{name}` permission. Overrides message delay, similarity threshold, etc.
2. **Rule Group** (`rules/groups.rs`) — reusable operator sets for the rules engine. Completely unrelated

These are NOT Vault groups. ChatControl does NOT use Vault group names. This is a deliberate design decision — works with any permissions plugin. Assign `chatcontrol.group.vip` permission to your Vault VIP group.

## Common Mistakes

- **First-match-wins ordering** — player gets the FIRST matching group only. Order groups from most specific (highest rank) to least. Admin should be listed before VIP if admin also has VIP permission
- **Channel delay overrides group delay** — per-channel `Message_Delay` takes priority over group-level delay. Users report "group delay setting not working" — check channel config
