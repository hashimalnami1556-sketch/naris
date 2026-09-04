# CALL OF NARIS — BATCH 10
## Environment Production Factory

**Status:** ACTIVE / PRODUCTION
**World focus:** W04 Ashen Forest first, then W01–W10 world factory expansion.

### Production output

1. Modular architectural kit: floors, walls, pillars, arches, doors, bridges, stairs, roofs and broken variants.
2. Terrain dressing: cliffs, rocks, roots, ash mounds, debris, bones and vegetation.
3. Hero landmarks: Waystones, portals, shrines, gates, arenas and traversal anchors.
4. PBR material families with tileable BaseColor, Normal, Roughness, AO and Height where appropriate.
5. Atmosphere presets: dawn, overcast, night, storm, fog and supernatural/aether variants.
6. Collision and navigation helpers for gameplay-ready assembly.
7. LOD policy and streaming-cell metadata.
8. Blender procedural factory for repeatable source generation.
9. Babylon/Unity/Unreal integration metadata without pretending a generated concept image is a final runtime mesh.

### W04 assembly order

`Terrain -> Primary architecture -> Traversal -> Landmarks -> Dressing -> Materials -> Lighting -> VFX -> NavMesh -> Collision -> LOD -> Streaming -> QA`

### Quality gates

- No visible modular seams at intended grid boundaries.
- Walkable surfaces have collision and navigation support.
- Hero landmarks receive bespoke silhouette and lighting treatment.
- Materials remain physically coherent under dawn/night/ash-storm lighting.
- No single mesh carries unnecessary material slots.
- Distant dressing receives LOD/impostor treatment.
- Environment remains readable during combat and traversal.
- VFX and fog cannot obscure critical navigation affordances.

### Source of truth

Machine-readable specifications live under `data/environments/`; procedural source lives under `tools/blender/`; final runtime assets are approved only after engine import and QA.

### Next production wave

W04 receives the highest asset density for the vertical slice. W01–W03 and W05–W10 use the same factory architecture but each receives a distinct visual language, material family, landmark grammar and atmospheric profile.
