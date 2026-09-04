# CALL OF NARIS — Batch 09 Asset & Environment Factory

Status: PRODUCTION READY / LOCKED
Target world: W04 Ashen Forest
Target engines: Unreal Engine 5 / Babylon.js / Unity 6 / Godot 4

## 1. Characters

### Ash Wanderer
- Role: DPS / Explorer
- IDs: NARIS-W04-CHR-ASHWANDERER-0001
- Requirements: full-body, front/back/side/3-quarter references; cloth simulation zones; Aether sockets; LOD0/1/2; humanoid rig.

### Marsh Seer
- Role: Support / Caster
- ID: NARIS-W07-CHR-MARSHSEER-0001
- Requirements: staff, ritual ornaments, emissive aether core, robe layers, caster hand sockets, LOD0/1/2.

### Castle Warden
- Role: Tank / Guardian
- ID: NARIS-W08-CHR-CASTLEWARDEN-0001
- Requirements: heavy armor, shield, weapon sockets, armored silhouette, LOD0/1/2.

### Translucent Hero
- ID: NARIS-W04-CHR-HERO-TRANSLUCENT-0001
- Material: translucent/ethereal with depth-fade, emissive rune channels and controlled rim glow.

### Gate Guardian
- ID: NARIS-W04-ENM-GATEGUARDIAN-0001
- Role: elite gate defender
- Material: spectral armor, emissive core, translucent secondary layer.

## 2. Props / interactables

- NARIS-W04-PRP-WAYSTONE-0001 — Waystone / Save Point
- NARIS-W04-PRP-HOLYPORTAL-0001 — Holy Transition Portal
- NARIS-W04-PRP-CHEST-0001 — Reward Chest
- NARIS-W04-PRP-SIGNPOST-0001 — Directional Signpost
- NARIS-W04-PRP-ASHLANTERN-0001 — Ash Lantern
- NARIS-W04-PRP-RITUALSTONE-0001 — Ritual Stone
- NARIS-W04-PRP-RUINARCH-0001 — Modular Ruin Arch
- NARIS-W04-PRP-BONEPILE-0001 — Bone Pile

## 3. Ashen Forest environment kit

### Gameplay locations
1. Forest Entrance
2. Broken Shrine
3. Ruined Bridge
4. Whisper Lake
5. Ash Gate
6. Bone Beast Arena

### Modular pieces
- Ground tile 1x1 / 2x2 / 4x4 m
- Cliff pieces: straight, corner, cap, transition
- Ruin walls: short, tall, damaged, doorway
- Arches: intact, broken, moss-covered
- Bridges: straight, collapsed, side rails
- Stairs: 1m / 2m / 4m rise
- Platforms and ledges
- Gate frames and portal sockets
- Collision-only traversal blockers

## 4. Materials

Tileable PBR stone master:
- BaseColor
- Normal
- Roughness
- AO
- Height
- optional packed ORM

Variants:
- weathered stone
- moss stone
- ash-covered stone
- wet stone
- ancient ruin stone
- corrupted stone

## 5. Vegetation / dressing

- dead oak
- burned roots
- ash grass
- ferns
- red-black shrubs
- fallen branches
- mushrooms / aether flora
- hanging vines
- bone debris
- ash piles

## 6. Procedural Babylon scene requirements

Every asset must expose:
- canonical asset ID
- transform-safe root
- socket names
- collision proxy
- LOD metadata
- material slots
- animation metadata where applicable
- interaction tags

Character switching must support:
`Ashen Vessel -> Ash Wanderer -> Marsh Seer -> Castle Warden`

The scene preview must load a common lighting rig, fog volume, camera bookmarks and a combat HUD test layer.

## 7. Quality gates

- silhouette readable at gameplay distance
- no broken normals
- no non-manifold critical geometry
- UVs within 0-1 unless explicitly tiled
- material instances named canonically
- LOD transitions tested
- collision tested
- sockets verified
- transparency sorting checked
- Nanite suitability checked for Unreal assets
- Babylon GLB export checked
- source file retained

## 8. Delivery structure

`assets/characters/`
`assets/enemies/`
`assets/weapons/`
`assets/props/`
`assets/environments/W04_AshenForest/`
`assets/materials/`
`assets/vfx/`
`data/asset_registry/`
`docs/batches/`

## 9. Acceptance

Batch is accepted when all listed assets have a canonical ID, production status, engine target, source reference, storage path, intended use, and QA state. Concept-only images are references; engine-ready status is granted only after mesh, material, rig/collision and runtime validation.
