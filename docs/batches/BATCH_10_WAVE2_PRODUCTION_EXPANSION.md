# CALL OF NARIS — BATCH 10 WAVE 2
## Environment Production Factory Expansion

**Status:** ACTIVE
**Priority:** HIGH
**Primary biome:** W04 Ashen Forest

## Production targets

Wave 2 raises W04 from a basic modular environment to a production-grade vertical-slice biome with authored density, traversal readability and landmark hierarchy.

### Environment layers

1. Terrain macroforms — slopes, ravines, plateaus, cliff shelves.
2. Traversal — roads, bridges, stairs, ledges, jump gaps and traversal anchors.
3. Architecture — shrine ruins, gothic arches, collapsed towers, buttresses and broken walls.
4. Caves — small and large cave mouths, columns, ceiling breaks, pools and root clusters.
5. Nature — burnt-tree families, roots, dead ferns, ash shrubs, ember moss and Aether flora.
6. Dressing — rubble, bones, carts, banners, weapons, logs, craters and environmental storytelling props.
7. Landmarks — Waystones, Holy Portal, Ash Gate, Ritual Arena and Spirit Crossing.
8. Water — Whisper Lake shore kit, shallow-water tiles and waterfall variants.
9. FX dressing — ashfall, embers, Aether motes, corruption patches and rune markers.

## Density rules

- Hero zone: bespoke assets and highest silhouette fidelity.
- Gameplay zone: repeated modular assets with controlled variation.
- Distant zone: LOD2/impostor-biased dressing.
- No dressing may block combat telegraphs, traversal routes or interaction points.

## Technical budgets

- Modular architecture uses the 2m production grid.
- Hero landmarks use 3 LOD tiers.
- Streaming cells target 32m.
- Main traversal width target: 2.2m minimum.
- Combat clearance target: 3.5m minimum.
- Material slots are minimized per mesh.

## Authoring pass

Each asset receives:

`Asset ID -> Category -> Pivot -> Grid -> Material Set -> Collision Class -> Nav Class -> LOD Policy -> Streaming Class -> Gameplay Tags`

## Approval gate

Concept art is reference only. An asset becomes runtime-approved after mesh validation, material validation, collision/navigation validation, engine import and in-scene QA.

## Next wave

After W04 Wave 2: caves and underground traversal, then W01/W02/W03 environment factory variants. W05–W10 inherit the same technical contract while retaining unique visual languages.
