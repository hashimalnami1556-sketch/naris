# NARIS Master Integration

## Vertical Slice
Ashen Forest Entrance -> Root Tunnel -> Aether Shrine -> Ash Gate -> Bone Beast Arena.

## Runtime ownership
- Combat: attack definitions, hit windows, hitboxes, boss phases.
- AI: threat selection, encounter pacing, enemy profiles.
- World: zones, dungeon/event generation, roads, weather, fast travel.
- Narrative: quest state, dialogue, schedules, codex, world consequences.
- Player/meta: inventory, save state, audio/quality/release gates.

## Integration rule
Systems communicate through typed IDs, gameplay tags, components/subsystems and interfaces. Avoid direct Blueprint casting between feature domains.

## Content-production gate
No placeholder `.uasset` files are included. Each binary asset must be authored/imported and saved by Unreal Editor so package metadata remains valid.
