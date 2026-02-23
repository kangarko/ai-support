---
name: chat-formatting
description: 'Troubleshooting format display, hover/click events, gradients, and color permissions'
---

# Chat Formatting Troubleshooting

## Common Mistakes

- **Gradients are "unsafe"** — MiniMessage tags inside `Message` break gradient rendering. Use gradients only on plain text without inner color/format tags
- **Only ONE `Run_Command` per format part** — Minecraft protocol limitation. Split into separate Parts if multiple click commands are needed
- **Hover max 21 chars pre-1.13** — older versions truncate hover text. Use shorter text for compatibility
- **`{player_prefix+}` vs `{player_prefix}`** — the `+` variant includes a trailing space. Without `+`, there's no separator between prefix and name
