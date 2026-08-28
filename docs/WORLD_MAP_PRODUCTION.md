# NARIS World & Map Production Standard

## World set

W01 Frozen Peaks · W02 Forge of Flame · W03 Echoes Desert · W04 Ashen Forest · W05 Silent Abyss · W06 Inverted Towers · W07 Lost Souls Swamp · W08 Astral Fortress · W09 Forgotten Canals · W10 Throne of Naris.

## Map hierarchy

`World → Region → Subregion → Encounter → Landmark → Traversal Link → Secret`

## Every region requires

- top-down macro map
- playable blockout
- traversal graph
- combat encounter map
- landmark list
- spawn/AI zones
- navigation constraints
- streaming boundaries
- environmental storytelling beats
- loot/reward placement
- quest hooks
- fast-travel or checkpoint logic where applicable

## Environment kit

Each world receives modular floors, walls, ceilings, arches, stairs, ramps, bridges, cliffs, transitions, doors, gates, pillars, hero landmarks, cover pieces, foliage/decals, destructibles and gameplay interactables.

## Technical-art requirements

Shipping geometry should use consistent pivots, metric scale, collision conventions, material slots, lightmap/UV policy where required, LODs and Nanite-compatible authoring where supported by the target runtime. Textures use a controlled PBR channel convention and shared master materials.

## Streaming and performance

Large worlds are divided into predictable streaming cells. High-cost hero assets are isolated from repeated modular assets. VFX, foliage and transparent materials receive separate budgets. Every region has a documented memory and frame-time target before content lock.

## Map naming

`NARIS-W<world>-MAP-<region>-<sequence>`

Example: `NARIS-W04-MAP-ASHENHEART-0001`

## Production gate

A map is not complete when the concept looks finished. It is complete when traversal, encounter flow, navigation, streaming, collision, quest hooks, landmarks, optimization and QA are all validated in the playable build.
