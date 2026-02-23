---
name: snowmen
description: 'Troubleshooting snowman protection, Psycho hostile snowmen, and mob transformation'
---

# Snowmen Troubleshooting

## Common Mistakes

- **Psycho NMS compatibility is limited** — only MC 1.8.8, 1.12, 1.16, 1.20.5+. Cauldron is explicitly excluded. On incompatible versions, a warning is logged and Psycho features silently disable
- **`Convert_Existing` is IRREVERSIBLE** — there is no undo. Users must restore from a world backup taken before enabling. Always warn about this
- **PsychoMob listener registered regardless of Psycho settings** — because `Convert_New`/`Convert_Existing` can be changed at runtime without restart, the listener is always active on compatible versions. This is intentional, not a bug

## Platform Notes

- Cauldron servers: explicitly excluded from Psycho features
- Paper/Spigot/Purpur: fully supported
