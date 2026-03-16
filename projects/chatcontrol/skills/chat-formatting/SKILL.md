---
name: chat-formatting
description: 'Troubleshooting format display, hover/click events, gradients, images in formats, and color permissions'
---

# Chat Formatting Troubleshooting

## Common Mistakes

- **Gradients are "unsafe"** — MiniMessage tags inside `Message` break gradient rendering. Use gradients only on plain text without inner color/format tags
- **Only ONE `Run_Command` per format part** — Minecraft protocol limitation. Split into separate Parts if multiple click commands are needed
- **Hover max 21 chars pre-1.13** — older versions truncate hover text. Use shorter text for compatibility
- **`{player_prefix+}` vs `{player_prefix}`** — the `+` variant includes a trailing space. Without `+`, there's no separator between prefix and name
- **`Message:` does NOT execute commands** — it only displays text. Users sometimes put `/chc a image ...` inside a `Message:` value expecting it to render images — it will print the command text literally. To show images in format parts, use the dedicated image keys below

## Images in Format Parts

Format parts support showing images alongside text using these keys:

| Key | Purpose | Example |
|-----|---------|--------|
| `Image_File` | Image from the `images/` folder | `creeper-head.png` |
| `Image_Head` | Player head from avatar API | `"{player}"` or `"Herobrine"` |
| `Image_Url` | Image from a remote URL | `"https://example.com/logo.png"` |
| `Image_Height` | Height in chat lines (default: 8, min: 2) | `10` |
| `Image_Type` | Filler character style | `BLOCK`, `DARK_SHADE`, `MEDIUM_SHADE`, `LIGHT_SHADE` |

**Only one image source allowed per part** — you cannot combine `Image_File`, `Image_Head`, and `Image_Url` in the same part.

Example — player head image in a MOTD format:
```yaml
Parts:
  Welcome:
    Message:
    - " Welcome back to MyServer {player}"
    - " Your return is appreciated!"
    Image_Head: "{player_name}"
    Image_Height: 10
```

Example — static image from file:
```yaml
Parts:
  Logo:
    Message: "Welcome to our server!"
    Image_File: "creeper-head.png"
    Image_Height: 8
```

The `/chc a image <file> <height> <message>` command is for **one-time broadcast announcements only** — it cannot be used inside format files.
