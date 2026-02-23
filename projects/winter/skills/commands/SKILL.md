---
name: commands
description: 'Troubleshooting Winter commands and platform compatibility'
---

# Commands Troubleshooting

## Common Mistakes

- **Folia and Luminol are explicitly unsupported** — plugin won't load. Use Paper, Spigot, or Purpur
- **`/winter populate` intentionally blocks the main thread** — it's synchronous by design. Console warnings about "server not responding" can be ignored. Wait for completion
- **`Terrain.Snow_Generation` does not support `/winter reload`** — requires a full server restart for changes to take effect. Users report "setting not working after reload" — this is the cause
