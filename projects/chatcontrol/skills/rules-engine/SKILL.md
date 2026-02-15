---
name: rules-engine
description: 'ChatControl rules engine: .rs rule files, regex matching, operators, conditions (require/ignore), actions (then replace/rewrite/warn/deny/kick), groups, rule types (chat/command/sign/book/anvil/tag), data persistence, delays. Use when working on rule code, writing custom rules, or diagnosing rule matching issues.'
---

# Rules Engine

## Overview

The rules engine processes chat messages, commands, signs, books, anvils, and tags through regex-based rules. Each rule has a match pattern, optional conditions (require/ignore), and action handlers (then). Rules are defined in `.rs` files under `rules/`. Reusable operator sets are called "groups" (defined in `groups.rs`).

## Architecture

### Key Classes
- `Rule` (operator/Rule.java) — individual rule with regex pattern, extends `RuleOperator`
- `RuleOperator` (operator/RuleOperator.java) — base providing require/ignore conditions and replace/rewrite actions
- `Operator` (operator/Operator.java) — universal base for all operators (timing, actions, data persistence)
- `Rules` (operator/Rules.java) — singleton loader/registry for all rules
- `Group` (operator/Group.java) — reusable operator set referenced by `group <name>`
- `Groups` (operator/Groups.java) — singleton loader for groups from `groups.rs`
- `RuleType` (core: model/RuleType.java) — enum: GLOBAL, CHAT, COMMAND, SIGN, BOOK, ANVIL, TAG

### Rule Processing Flow
```
Message/command/sign/book/anvil/tag input
  → Rules.getRules(type) loads rules for this type
    → For each rule (top to bottom):
      1. @import: imported rules checked first
      2. Compile matcher (apply strip colors/accents if set)
      3. Match regex against message
      4. If match: fire PreRuleMatchEvent (API — cancellable)
      5. Check require/ignore conditions (canFilter())
      6. Execute rule operators (executeOperators())
      7. Execute group operators if `group <name>` set
      8. If `then abort`: stop processing remaining rules
```

## Common Issues & Solutions

### "Rule isn't matching"
1. Enable `Rules.Verbose: true` in settings.yml for match logs
2. Test regex at regex101.com (use Java/PCRE flavor)
3. Check `Rules.Apply_On` includes the type
4. Verify `strip colors` isn't removing needed characters
5. Check rule order — earlier rules with `then abort` may stop processing
6. Check `ignore string` isn't excluding the input

### "Group operators not executing"
1. Verify group name exists in `groups.rs` (case-sensitive)
2. Group operators execute AFTER rule-level operators
3. Groups cannot reference other groups (no nesting)
4. Groups don't support `ignore type` operator

### "Replace not working correctly"
- `then replace` replaces the MATCHED portion only, not full message
- `then rewrite` replaces the ENTIRE message
- `@prolong *` creates asterisks matching the matched text length
- Replacements happen in rule order (later rules see modified text)

### "JavaScript condition errors"
- Scripts see fully variable-replaced text, logged on error for debugging
- Must return boolean (`true`/`false`)
- Player context: `{player}` object available

### "Rules applying to Discord messages"
- Add `ignore discord` to rules that shouldn't affect Discord input
- Use `require discord` for Discord-only rules

## Key File Paths

- Rule class: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/operator/Rule.java`
- Operator base: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/operator/Operator.java`
- Rules manager: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/operator/Rules.java`
- Groups: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/operator/Groups.java`
- Rule files: `chatcontrol-bukkit/src/main/resources/rules/`
- Foundation RuleSetReader: `foundation-core/src/main/java/org/mineacademy/fo/model/RuleSetReader.java`

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
