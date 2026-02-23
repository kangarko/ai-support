---
name: private-messaging
description: 'Troubleshooting /tell, /reply, /ignore, PM formatting, social spy, and mail delivery'
---

# Private Messaging Troubleshooting

## Common Mistakes

- **Ignore checking is bidirectional** — if EITHER player ignores the other, PM is blocked. Users report "can't message player" — check both directions
- **`Sender_Overrides_Receiver_Reply` config option** — when true, sending a PM updates the receiver's reply target. When false, receiver must explicitly `/reply`. Users report "reply goes to wrong person"
- **Reply target expires on disconnect** — if the other player disconnects, `/reply` has no target. Users report "can't reply after they reconnected"
- **Vanish status synced via `SyncType.VANISH`** — vanished players appear offline to non-staff. `chatcontrol.bypass.vanish` sees vanished players
- **`Mail.Clean_After` purges old mail** — users report "mail disappeared" — check the cleanup period
- **Console PM forwarding limitation** — requires ≥1 online player (Bukkit limitation, same as proxy)
