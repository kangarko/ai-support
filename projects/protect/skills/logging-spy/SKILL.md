---
name: logging-spy
description: 'Troubleshooting command spy, transaction logging, and database log browsing'
---

# Logging & Spy Troubleshooting

## Diagnostic Flow — "Commands/transactions not being logged"

1. For commands: check `Command_Log.Enabled: true`, verify regex in `Command_List` matches, check player doesn't have `protect.bypass.command`
2. For transactions: check `Transaction_Log.Enabled: true` — **requires full server restart** (not reload)
3. For Discord: verify DiscordSRV installed and channel name matches exactly

## Common Mistakes

- **8 specific shop plugins supported** — BlueShop 3, ChestShop, EconomyShopGUI, ExcellentShop, QuickShop, ShopGUI+, Shop, SignShop. Other shops won't log transactions
- **Command spy auto-escapes leading `/`** — the initial `/` or `//` is automatically handled in regex patterns. Users don't need to escape it manually
- **`Transaction_Log` requires full restart** — not just reload. Users report "transactions not logging after changing config" — they need to restart
- **`/protect export` and `/protect import` require modern MC** — needs `Bukkit.getUnsafe().serializeItemAsJson()` support. Older MC versions will error
