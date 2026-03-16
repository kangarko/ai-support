---
name: books-announcements
description: 'Troubleshooting timed announcements, MOTD, books, images, and scheduled broadcasts'
---

# Books & Announcements Troubleshooting

## Common Mistakes

- **Timed messages skip first run after reload** — prevents spam on `/chc reload`. Users report "announcement didn't show after reload" — it will show on the next cycle
- **MOTD needs slight delay for client readiness** — set `Motd.Delay: 1 second` minimum. Without delay, the book may not display because the client isn't ready
- **Book limits: 100 pages, 256 chars per page** — Minecraft protocol limits. Exceeding these causes errors
- **Timer resets on `/chc reload`** — all announcement cycle states reset, and the first run is skipped (see above)
- **`/chc a image` is for one-time broadcasts only** — it sends an image announcement immediately to all online players. It cannot be placed inside format files or MOTD configs. To show images in MOTD or other formats, use `Image_File`, `Image_Head`, or `Image_Url` keys on the format part (see chat-formatting skill)
