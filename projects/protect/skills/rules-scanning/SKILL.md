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

- **NEVER ship new scan rules with destructive actions enabled by default** — Rules using `then confiscate`, `then strip-nbt`, or `then strip-attributes` must ALWAYS be commented out in `rules/main.rs` when shipped as defaults. Most Minecraft servers use custom items, RPG plugins, or custom enchantments that would be destroyed by aggressive rules. New rules should be provided as commented-out examples for admins to enable manually. Similarly, new scan triggers (e.g. Gamemode_Change, Creative_Click) must default to `false` in `settings.yml`. This was learned the hard way in 2.7.1 → hotfixed in 2.7.3.
- **`then confiscate excess` MUST be paired with `ignore inventory amount`** — without the amount threshold, excess confiscation has no reference point. Users report "confiscated everything instead of excess"
- **mcMMO items with "mcMMO Ability Tool" lore are auto-skipped** — the plugin also checks `McMMOHook.isUsingAbility()`. Users report "mcMMO items not being scanned" — this is intentional
- **Rule names must be globally unique across ALL `.rs` files** — not just within one file. Duplicate names silently override earlier rules
- **`Custom_Persistent_Tags: true` is the fix for custom plugin items being confiscated** — many plugins add persistent data tags to items. Enable this to skip items with custom tags. Use `/protect iteminfo nbt` to inspect items
- **Debug `[scan]` shows "Checking rule" not "Matched rule"** — the scan debug fires when the material pattern matches (`match *` = every item), NOT when the item violates the rule. The actual violation check is `canFilter()` which runs after. If users see all rules listed for all items, this is normal — add `operator` to Debug to see the actual filtering logic
- **1.20.5+ `max_stack_size` component bypasses `check stack size`** — hacked items can set a custom `max_stack_size` component (e.g. 99 on TOTEM_OF_UNDYING). Protect must compare against `Material.getMaxStackSize()` (vanilla default), not `ItemStack.getMaxStackSize()` (respects hacked component). Fixed in PR #72. The `over-64` rule with `require amount 65` can independently catch these items since it doesn't use `check stack size`
