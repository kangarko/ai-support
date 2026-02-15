---
name: books-announcements
description: 'ChatControl books and announcements: timed announcements, MOTD, broadcast, announcement types (CHAT/TITLE/ACTIONBAR/BOSSBAR/TOAST/IMAGE), books, auto-broadcast scheduling. Use when diagnosing announcement display, book authoring, MOTD, or scheduled broadcast issues.'
---

# Books & Announcements

## Overview

ChatControl supports timed announcements in 6 display types, book-based rich text (MOTD, help books), and broadcast commands. Announcements cycle through message groups on configurable schedules.

## Architecture

### Key Classes
- `Announce` (model/Announce.java) — announcement scheduling engine
- `AnnounceType` — enum: `CHAT`, `IMAGE`, `TITLE`, `ACTIONBAR`, `BOSSBAR`, `TOAST`
- `CommandAnnounce` (command/CommandAnnounce.java) — `/chc announce` subcommand
- `Book` (model/Book.java) — book loading and display
- `CommandMotd` (command/CommandMotd.java) — MOTD display
- `SimpleBook` (Foundation) — low-level book API

### Announcement Types
| Type | Description | Example |
|------|-------------|---------|
| `CHAT` | Regular chat message(s) | Multi-line text with formatting |
| `IMAGE` | ASCII art image in chat | Logo/banner display |
| `TITLE` | Full-screen title + subtitle | Big announcement overlay |
| `ACTIONBAR` | Text above hotbar | Subtle notification |
| `BOSSBAR` | Boss bar at top | Timed bar with color/style |
| `TOAST` | Achievement popup | Toast notification |

### Announcement Flow
```
Server startup
  → Announce.start() schedules repeating task
    → Every tick period:
      1. Select next announcement group (round-robin per player OR random)
      2. Filter eligible players (permissions, worlds, toggles)
      3. For each player, check conditions
      4. Display using AnnounceType handler
      5. Track last-shown index per player
```

## Common Issues & Solutions

### "Announcements not showing"
1. Check `Announcements.Enabled: true` in settings.yml
2. Verify `Delay` isn't too long for testing
3. Check player is in correct `Worlds` (if configured)
4. Check player has required `Permission` (if configured)
5. Check player hasn't toggled off: `/toggle announcement`
6. At least 2 players needed? No — works with 1+

### "Announcements show to wrong players"
- Check `Worlds` filter in announcement config
- Check `permission` in announcement group
- Check `condition` operators in .rs file

### "Book formatting broken"
- YAML multi-line: use `|` for pages
- Colors: `&` codes or MiniMessage
- Click actions: `[text](run_command:/cmd)`
- Max 100 pages, 256 chars per page (Minecraft limit)

### "MOTD not showing on join"
1. `Motd.Enabled: true`
2. `Motd.Delay: 1 second` — needs slight delay for client readiness
3. Book file must exist in `books/` directory
4. Book name in `Motd.Format` must match filename (without .yml)

### "Boss bar disappears too fast"
- Set `seconds` in the bossbar announcement group
- Default is short; increase for longer display

### "Image announcement not rendering"
- Image must be defined in image map
- ASCII art rendered from stored pixel data
- Check console for image loading errors

## Key File Paths

- Announce: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/model/Announce.java`
- Book: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/model/Book.java`
- CommandAnnounce: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/command/CommandAnnounce.java`
- CommandMotd: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/command/CommandMotd.java`
- Book files: `chatcontrol-bukkit/src/main/resources/books/`
- Announcement messages: `chatcontrol-bukkit/src/main/resources/messages/`
- Settings: `chatcontrol-bukkit/src/main/resources/settings.yml` (Announcements, Motd)

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
