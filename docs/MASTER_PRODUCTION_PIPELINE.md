# CALL OF NARIS — Master Production Pipeline

## Purpose

This document is the production contract for turning NARIS from a collection of prototypes into a single traceable game-production system.

## Canonical stack

| Layer | System | Canonical responsibility |
|---|---|---|
| Planning | Slack | Decisions, assignments, production coordination |
| UX/UI | Figma | Interaction flows, HUD, menus, design system |
| Visual concept | Adobe / CreativeClaw / Apixel / OpenArt / Higgsfield | Concept art, keyframes, visual exploration |
| 3D conversion | to3D | 2D-to-3D starting geometry and export formats |
| 3D production | Blender / Unreal pipeline | Retopology, UV, materials, LOD, collision, rigging |
| Video | Higgsfield / Visla / VideoZero | Cinematics, trailer, motion graphics and marketing video |
| Documentation | GitHub | Versioned source of truth |
| Asset registry | Production registry schema | Asset IDs, dependencies, status, ownership and QA |
| Analytics | PostHog | Playtest telemetry, funnels, crashes and balancing signals |
| Security | Bitdefender | Link/file safety checks before external ingestion |
| Publishing | GitHub + engine build pipeline | Release candidates and reproducible builds |

## Canonical asset lifecycle

`BRIEF → CONCEPT → APPROVAL → ASSET_ID → SOURCE → MODEL/ART → MATERIAL → RIG/ANIMATION → ENGINE → OPTIMIZATION → QA → APPROVED → RELEASE`

No asset is release-ready until all mandatory gates are represented in the registry.

## Asset ID

Format:

`NARIS-W<world>-<domain>-<type>-<sequence>`

Examples:

- `NARIS-W04-CHR-HERO-0001`
- `NARIS-W04-ENM-BONEBEAST-0001`
- `NARIS-W04-WPN-MACE-0001`
- `NARIS-W04-ENV-KIT-0001`
- `NARIS-W04-VFX-EMBER-0001`

## Production domains

`CHR` Characters  
`ENM` Enemies  
`BOS` Bosses  
`WPN` Weapons  
`PRP` Props  
`ENV` Environment  
`MAT` Materials  
`VFX` Visual effects  
`UI` Interface  
`MAP` Maps  
`CINE` Cinematics  
`AUD` Audio  
`QST` Quests/content

## World matrix

| ID | World | Signature |
|---|---|---|
| W01 | Frozen Peaks | ice, avalanches, frozen ruins |
| W02 | Forge of Flame | volcanic industry, molten metal |
| W03 | Echoes Desert | dunes, buried cities, sound anomalies |
| W04 | Ashen Forest | ash, ruins, mist, corrupted wildlife |
| W05 | Silent Abyss | deep darkness, pressure, bioluminescence |
| W06 | Inverted Towers | impossible architecture, gravity shifts |
| W07 | Lost Souls Swamp | spectral wetlands, drowned ruins |
| W08 | Astral Fortress | celestial stone, void bridges, star energy |
| W09 | Forgotten Canals | ancient waterways, machinery, flooded districts |
| W10 | Throne of Naris | royal ruins, cosmic corruption, final citadel |

## Character production baseline

### Ashen Vessel

- Height: 183 cm
- Athletic body type
- Burned cloak
- Ancient armor
- Ember veins
- Runic scars
- Flame Relic Sword
- Gameplay readability target: clear silhouette at 20–30 m

### Celestial Wolf

- Astral companion
- Silver-white spectral fur
- Celestial blue energy
- Roles: guide, tracker, guardian, lore keeper
- Abilities: Soul Vision, Astral Dash, Echo Link, Celestial Roar

### Enemy families

- Bone Beast
- Fallen Warden
- Mist Guardian
- Ash Giant
- Veil Mother
- Celestial/astral corrupted creatures
- Human/guardian variants per world

## Weapon baseline

- Sword of Poem
- Flame Relic Sword
- Mist Bow
- Aether Dagger
- Void Scythe
- Ash Spear
- Naris Hammer
- Heavy mace/club enemy archetype

Every weapon requires: concept, orthographic reference, dimensions, grip point, pivot, hit frames, collision, damage profile, material definition, LODs, VFX hooks, audio hooks, and engine metadata.

## Environment production baseline

Each world receives a modular kit containing:

- ground tiles
- cliff/wall modules
- transitions
- doors/gates
- stairs/bridges
- landmark architecture
- vegetation/organic set
- debris/decals
- interactable props
- destructible variants
- collision meshes
- LODs
- master materials
- lighting presets
- VFX ambience
- encounter arenas
- traversal routes

## Maps

Every world must have:

1. World map
2. Region map
3. Encounter map
4. Quest markers
5. Fast-travel nodes
6. Secret routes
7. Collectible/lore locations
8. Boss arena
9. Save/checkpoint locations
10. Navigation metadata

## QA gates

- visual quality
- silhouette readability
- collision correctness
- animation deformation
- material consistency
- LOD correctness
- memory budget
- frame-time budget
- gameplay behavior
- accessibility
- localization
- save/load integrity
- telemetry event validity
- platform build validation

## Important production rule

Do not confuse a generated concept with a finished game asset. Generated images are references until they pass modeling, technical-art, engine, performance and QA gates.
