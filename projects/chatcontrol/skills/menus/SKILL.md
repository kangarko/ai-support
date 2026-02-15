---
name: menus
description: 'ChatControl GUI menus: color picker menu, spy toggle menu, channel list menu, Foundation Menu system, menu configuration, click actions, animated menus, paged menus. Use when diagnosing menu display, GUI interaction, or menu configuration issues.'
---

# GUI Menus

## Overview

ChatControl uses Foundation's menu framework to provide interactive inventory GUIs: color picker, spy toggle, channel browser, and more. Menus are Java-based using Foundation's `Menu`, `MenuPagged`, and `MenuStandard` classes.

## Architecture

### Key Classes
- `ColorMenu` (menu/ColorMenu.java) — color/decoration picker using wool/carpet items
- `SpyMenu` (menu/SpyMenu.java) — toggle spy on different message types
- `ChannelMenu` — channel listing/joining GUI
- `Menu` (Foundation) — base menu class with inventory management
- `MenuPagged<T>` (Foundation) — paginated menu for lists
- `MenuStandard` (Foundation) — standard single-page menu

### Foundation Menu System
```
Menu (abstract)
  ├── MenuStandard — fixed layout menu
  ├── MenuPagged<T> — auto-paginated list menu
  ├── MenuQuantifiable — number selection
  └── MenuContainerChances — weighted random items
```

### Menu Lifecycle
```
Player clicks command/item
  → Menu.displayTo(player)
    1. Create inventory (size, title)
    2. Call getItemAt(slot) for each slot
    3. Register click listeners
    4. Show to player

Player clicks slot
  → onMenuClick(player, slot, action, clickedItem)
    1. Cancel vanilla click (prevent item removal)
    2. Process custom logic
    3. Update display or close
```

## Common Issues & Solutions

### "Menu not opening"
1. Check command permission (`chatcontrol.command.color`, `chatcontrol.command.spy`)
2. Check for console errors on menu open
3. Inventory size must be multiple of 9 (max 54)
4. Title max 32 chars (pre-1.20) or longer (1.20+)

### "Menu items missing"
1. Check player has required permissions for items
2. Paged menu: check if items are on another page
3. Color menu: player needs `chatcontrol.color.<color>` permissions
4. Spy menu: player needs `chatcontrol.spy.<type>` permissions

### "Clicking does nothing"
1. Menu may need `restartMenu()` call to update
2. Check for errors in console on click
3. Verify click handler slot numbers match item positions
4. Inventory click event might be cancelled by another plugin

### "Items can be taken from menu"
- Foundation menus cancel clicks by default
- If items are removable, another plugin may be interfering
- Check for conflicting inventory event listeners

### "Menu flickers/refreshes constantly"
- Animated title updates cause brief flicker
- `restartMenu()` in a loop causes rapid refreshing
- Use targeted slot updates instead of full restart when possible

## Key File Paths

- ColorMenu: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/menu/ColorMenu.java`
- SpyMenu: `chatcontrol-bukkit/src/main/java/org/mineacademy/chatcontrol/menu/SpyMenu.java`
- Menu (Foundation): `Foundation/foundation-bukkit/src/main/java/org/mineacademy/fo/menu/Menu.java`
- MenuPagged: `Foundation/foundation-bukkit/src/main/java/org/mineacademy/fo/menu/MenuPagged.java`
- MenuStandard: `Foundation/foundation-bukkit/src/main/java/org/mineacademy/fo/menu/MenuStandard.java`
- ItemCreator: `Foundation/foundation-bukkit/src/main/java/org/mineacademy/fo/menu/model/ItemCreator.java`
- Settings: `chatcontrol-bukkit/src/main/resources/settings.yml` (Color, Spy sections)

## Reference

For configuration keys, default values, commands, permissions, and variables not covered above, read the source files directly using `read_codebase_file`. The key file paths above point to the most relevant files.
