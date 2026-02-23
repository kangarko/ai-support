---
name: rules-scanning
description: 'Troubleshooting rule matching, scanning triggers, and item confiscation issues'
---

# Rules & Scanning Troubleshooting

## Diagnostic Flow — "Rule not triggering / wrong items confiscated"

1. Enable `Debug: [scan, operator]` and check console output
2. Check rule has a unique `name` (globally unique across ALL `.rs` files)
3. Check material name matches (case-sensitive, UPPER_CASE Bukkit names)
4. Check global `Ignore` settings aren't suppressing the scan

## Common Mistakes

- **`then confiscate excess` MUST be paired with `ignore inventory amount`** — without the amount threshold, excess confiscation has no reference point. Users report "confiscated everything instead of excess"
- **mcMMO items with "mcMMO Ability Tool" lore are auto-skipped** — the plugin also checks `McMMOHook.isUsingAbility()`. Users report "mcMMO items not being scanned" — this is intentional
- **Rule names must be globally unique across ALL `.rs` files** — not just within one file. Duplicate names silently override earlier rules
- **`Custom_Persistent_Tags: true` is the fix for custom plugin items being confiscated** — many plugins add persistent data tags to items. Enable this to skip items with custom tags. Use `/protect iteminfo nbt` to inspect items
