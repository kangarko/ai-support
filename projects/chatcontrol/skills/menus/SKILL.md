---
name: menus
description: 'Troubleshooting GUI menus: color picker, spy toggle, and menu interaction issues'
---

# Menu Troubleshooting

## Common Mistakes

- **Title max 32 chars pre-MC 1.20** — longer titles cause errors on older versions. MC 1.20+ supports longer titles
- **Animated title causes flicker** — `restartMenu()` in a loop causes rapid refreshing. Use targeted slot updates instead of full restart when possible
- **Color/spy menu items need specific permissions** — `chatcontrol.color.{color}` for color menu items, `chatcontrol.spy.{type}` for spy menu items. Items without permission are hidden
