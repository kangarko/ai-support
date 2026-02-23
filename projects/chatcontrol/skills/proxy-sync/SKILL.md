---
name: proxy-sync
description: 'Troubleshooting BungeeCord/Velocity proxy sync, cross-server messaging, and data synchronization'
---

# Proxy Sync Troubleshooting

## Diagnostic Flow — "Proxy sync not working"

1. Check `proxy.yml` → `Enabled: true`
2. Verify `Server_Name` matches EXACTLY — velocity.toml `[servers]` key or BungeeCord config
3. Check proxy plugin (chatcontrol-bungeecord or chatcontrol-velocity) is installed
4. Restart required after proxy.yml changes (no live reload)

## Common Mistakes

- **Plugin messages limited to 32,767 bytes** — extremely large player data (many channels, ignore lists) is silently truncated. Logged once per 5 minutes when this happens
- **`PendingProxyJoinTask` retries every 0.5s until DB ready** — users report "data missing on server switch" because the database hasn't loaded yet. Check for slow DB warnings (>100ms connections)
- **Console forwarding requires ≥1 online player** — Bukkit limitation. If the server has 0 players, console messages can't be forwarded via plugin messaging
- **Server names must be alphanumeric + underscores only** — special characters cause parsing failures
