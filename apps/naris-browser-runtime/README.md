# NARIS REALMS — Browser Runtime v2

Babylon.js + React 19 + TypeScript runtime foundation for **The Ashen Awakening**.

## Runtime boundary
- **React:** HUD, menus and accessibility-facing controls.
- **Babylon.js:** world, camera, player, enemies, lighting and render loop.
- **GameState:** serializable simulation state; renderer objects are never saved.
- **GameBus:** typed gameplay events between systems.
- **ServiceRegistry:** explicit dependency boundary.

## Current slice
- Ashen Forest procedural hero scene.
- Unified character controller for Ash / Rune / Kor.
- Keyboard movement, attack and character switching.
- Three enemy archetypes with chase/attack behavior.
- Typed combat events and player damage state.
- Cinematic RTL HUD with responsive mobile layout.

## Next integration gates
1. Waystone activation + autosave.
2. Shard collection + quest objective tracking.
3. Boss controller and phase pipeline.
4. Wolf companion runtime.
5. GLB asset manifest/loading and LOD policy.
6. Mobile touch controls + quality manager.
7. Playtest and performance gate.

This scaffold deliberately keeps procedural geometry as a runtime blocker until approved production meshes are imported; it does not represent final art quality.
