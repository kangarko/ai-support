---
name: private-messaging
description: 'ChatControl private messaging: /tell, /reply, /ignore, PM formatting, social spy, vanish handling, proxy PMs, PM toggle, auto-responder, mail system. Use when diagnosing private message issues, PM formatting, ignore/spy, or mail delivery.'
---

# Private Messaging & Mail

## Overview

ChatControl provides `/tell` and `/reply` for private messages with custom formatting, social spy, ignore lists, vanish checking, and proxy support. The mail system allows offline message delivery.

## Architecture

### Key Classes
- `PrivateMessage` (model/PrivateMessage.java) — PM sending logic
- `CommandTell` (command/CommandTell.java) — `/tell` command
- `CommandReply` (command/CommandReply.java) — `/reply` command
- `CommandIgnore` (command/CommandIgnore.java) — `/ignore` command
- `CommandMail` (command/CommandMail.java) — `/mail` command
- `Mail` (model/db/Mail.java) — mail database row

### PM Send Flow
```
/tell <player> <message>
  → CommandTell validates args
    → PrivateMessage.send(sender, receiverCache, message)
      1. Check permissions (write, links)
      2. Strip unauthorized colors
      3. Check receiver not self
      4. Check receiver not vanished (unless bypass)
      5. Check ignore list (bidirectional)
      6. Check receiver has PMs enabled (ToggleType.PRIVATE_MESSAGE)
      7. Check sender has PMs enabled
      8. Filter through rules (Checker)
      9. Fire PrePrivateMessageEvent (API — cancellable)
      10. Format and send to sender (Format_Sender)
      11. Format and send to receiver (Format_Receiver)
      12. Format and send to console (Format_Console)
      13. Show toast notification (if enabled)
      14. Play sound (if configured)
      15. Update reply targets
      16. Log and broadcast to spies
      17. Send to proxy (if enabled)
```

## Common Issues & Solutions

### "Can't send PM — 'player is ignoring you'"
1. Check if sender is in receiver's ignore list
2. Check if receiver is in sender's ignore list
3. `chatcontrol.bypass.reach` bypasses ignore

### "PM not delivered — 'player has PMs disabled'"
- Receiver toggled off PMs: `/toggle private_message`
- `chatcontrol.bypass.reach` bypasses toggle

### "Can't PM vanished player"
- Vanished players appear offline to non-staff
- `chatcontrol.bypass.vanish` sees vanished players
- Proxy: vanish status synced via SyncType.VANISH

### "Reply not working"
- Reply target expires on disconnect
- `Sender_Overrides_Receiver_Reply: true` — sender PM updates receiver's reply target
- Both sender and receiver track reply separately in PlayerCache

### "Proxy PMs not working"
1. `Private_Messages.Proxy: true` in settings.yml
2. Proxy plugin installed on BungeeCord/Velocity
3. Same `Server_Name` in proxy.yml across servers
4. Uses `ChatControlProxyMessage.MESSAGE` for forwarding

### "Mail not delivered to offline player"
1. Check `Mail.Forward_Using_Proxy` if on network
2. Verify player exists in database
3. Check `Mail.Clean_After` hasn't purged old mail
4. Recipient gets notification on next login

## Key File Paths

- PrivateMessage: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/model/PrivateMessage.java`
- Tell: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/command/CommandTell.java`
- Reply: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/command/CommandReply.java`
- Ignore: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/command/CommandIgnore.java`
- Mail: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/command/CommandMail.java`
- Mail storage: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/model/db/Mail.java`
- PM formats: `chatcontrol-bukkit/src/main/resources/formats/pm-sender.yml`, `pm-receiver.yml`
- Settings: `chatcontrol-bukkit/src/main/resources/settings.yml` (Private_Messages, Mail)

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
