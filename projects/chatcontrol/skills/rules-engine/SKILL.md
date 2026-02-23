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

- **`then replace` vs `then rewrite`** — `replace` replaces only the MATCHED portion. `rewrite` replaces the ENTIRE message. Users often use `replace` expecting full-message replacement
- **`@prolong *` asterisk length matching** — generates asterisks matching the length of the matched text. Not intuitive
- **Groups can't nest** — a group cannot reference another group
- **Groups don't support `ignore type`** — type filtering must be done at the rule level
- **`ignore discord` operator** — prevents rules from applying to Discord-sourced messages
- **Replacements accumulate across rules in order** — later rules see the already-modified text. Rule ordering matters for chained replacements
