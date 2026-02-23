---
name: snow-weather
description: 'Troubleshooting snow particles, terrain generation, weather control, and performance issues'
---

# Snow & Weather Troubleshooting

## Diagnostic Flow — "Snow effects not working"

1. **Which system?** Particles (cosmetic), terrain snow (block changes), or weather control?
2. For particles: check `Snow.Enabled`, player world, and `/winter snow` toggle
3. For terrain: check `Terrain.Snow_Generation.Enabled` — requires server restart, not reload

## Common Mistakes

- **Particles auto-reduced to 8 on low TPS** — users report "fewer particles than configured" during lag. This is intentional performance protection
- **`Weather.Disable: true` overrides `Snow_Storm`** — these are mutually exclusive. Set `Weather.Disable: false` to use Snow_Storm
- **`Only_Melt_Unnatural_Snow` skips Y>90 mountain biomes** — prevents melting naturally snowy areas. Users report "snow not melting in mountains" — this is by design
- **`Freeze_Ignore` prevents water freezing near specific crop+neighbor combos** — protects farms from ice. Users report "water not freezing near my farm" — check this setting

## Performance Tuning

- Target: **<1.5ms for particle render** — use `Debug: [lag-particle]` to measure
- Reduce `Amount`, increase `Period_Ticks`, reduce `Range.Horizontal` / `Range.Vertical`, reduce `Radius` for terrain
- **Snow_Generation changes require full restart** — won't apply with `/winter reload`
