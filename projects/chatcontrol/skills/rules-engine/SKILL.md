---
name: rules-engine
description: 'Troubleshooting rule matching, replace vs rewrite, groups, and rule processing order'
---

# Rules Engine Troubleshooting

## Diagnostic Flow — "Rule isn't matching"

1. Enable `Rules.Verbose: true` in settings.yml for match logs
2. Test regex at regex101.com (Java/PCRE flavor)
3. Check rule order — earlier rules with `then abort` stop processing remaining rules
4. Check `ignore string` isn't excluding the input

## Common Mistakes

- **`#`-prefixed lines are COMMENTS — inactive at runtime.** In `.rs` files, any line whose first non-whitespace character is `#` is a comment. The shipped default rule files (`command.rs`, `chat.rs`, `private.rs`, `signs.rs`, etc.) deliberately ship many example rules pre-commented as opt-in templates (`/helpop`, `/nick` alias, `/op` blocker, `/gm` blocker, etc.). Users must remove the leading `#` from every line of the rule (the `#match`, `#then`, `#require`, `#ignore`, `#name`, `#strip`, `#dont`, `#group` lines) and run `/chc reload` to activate. Before telling a user a default rule 'just works', open the file and verify the rule's `match`/`then` lines are NOT prefixed with `#`. Same applies to commented-out keys in YAML configs.
- **`then replace` vs `then rewrite`** — `replace` replaces only the MATCHED portion. `rewrite` replaces the ENTIRE message. Users often use `replace` expecting full-message replacement
- **`@prolong *` asterisk length matching** — generates asterisks matching the length of the matched text. Not intuitive
- **Groups can't nest** — a group cannot reference another group
- **Groups don't support `ignore type`** — type filtering must be done at the rule level
- **`ignore discord` operator** — prevents rules from applying to Discord-sourced messages
- **Replacements accumulate across rules in order** — later rules see the already-modified text. Rule ordering matters for chained replacements
- **`require script` runs on Nashorn and cannot reach third-party plugin classes.** Nashorn resolves `Java.type("...")` (and bare class refs) through the thread context classloader that was active when the engine was created, which on Foundation is ChatControl's own Bukkit `PluginClassLoader`. That loader only delegates to other plugins listed in ChatControl's `plugin.yml` under `depend` / `softdepend` / `loadbefore`. Third-party plugin APIs (`com.gmail.nossr50.api.PartyAPI`, `com.palmergames.bukkit.towny.TownyAPI`, `me.clip.placeholderapi.PlaceholderAPI`, `me.angeschossen.lands.api.LandsIntegration`, anything from another plugin) are not in that list, so any script referencing them throws `ClassNotFoundException` regardless of whether the target plugin is installed. NEVER suggest a `require script` rule that calls a third-party plugin API as a workaround. Safe references inside scripts: `player` (the implicit sender variable), the `java.*` standard library, `org.bukkit.*` core API, and ChatControl's own shaded classes. For per-plugin checks (party membership, faction, town, claim, etc.) ChatControl already exposes them as channel `Party:` types or as built-in operators. If neither covers the use case, the answer is "this needs a code change", not a workaround script.
