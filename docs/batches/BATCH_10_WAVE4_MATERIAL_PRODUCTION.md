# CALL OF NARIS — BATCH 10 / WAVE 4
## Material Production Pass

**Status:** ACTIVE / PRODUCTION
**World:** W04 — Ashen Forest
**Material system:** PBR-first procedural authoring

## Delivered

The W04 material layer is now defined as a production factory rather than a list of visual ideas.

### Core materials
1. `MAT_W04_ASH_SOIL_01` — terrain, ash, charcoal micro detail.
2. `MAT_W04_VOLCANIC_STONE_01` — ruined stone, fractured volcanic surfaces.
3. `MAT_W04_ANCIENT_STONE_01` — hero Naris architecture, worn rune channels.
4. `MAT_W04_WET_STONE_01` — Whisper Lake shoreline and submerged stone.
5. `MAT_W04_BURNT_WOOD_01` — charred trunks, roots and structural timber.
6. `MAT_W04_OXIDIZED_IRON_01` — chains, gates, weapons and ruined metal.
7. `MAT_W04_AETHER_CRYSTAL_01` — emissive cyan spirit/aether crystal.
8. `MAT_W04_AETHER_CORRUPTED_STONE_01` — supernatural corruption and fault zones.
9. `MAT_W04_MOSS_LICHEN_01` — low-growth vegetation detail.
10. `MAT_W04_WHISPER_LAKE_01` — water surface with layered normals, transmission and coating.

### Decal family
- ash streak
- water stain
- ancient crack
- faded Naris rune
- burn scorch
- claw scratch
- aether corruption

## Material rules

- PBR values remain physically plausible.
- Metallic is reserved for conductive/metal surfaces.
- Emission is reserved for magic, aether and supernatural readability.
- Detail noise is separated from macro variation so the same material can serve multiple meshes.
- All materials are deterministic and can be regenerated from the factory seed.
- Material variants preserve the W04 palette instead of introducing random colors.
- Material slots remain intentionally small for runtime performance.

## Runtime intent

The procedural Blender materials are the authoritative look-development source. They can be converted/baked to standard BaseColor/Normal/Roughness/AO/Height texture sets when engine-native texture assets are required.

Target mapping:

| W04 material | UE5 | Unity 6 | Babylon.js |
|---|---|---|---|
| Ash Soil | Landscape/Material Instance | Lit terrain | PBRMaterial |
| Volcanic Stone | Master Material instance | URP/HDRP Lit | PBRMaterial |
| Ancient Stone | Hero material instance | HDRP Lit | PBRMaterial |
| Wet Stone | Water-edge instance | Lit + coat | PBRMaterial |
| Burnt Wood | Foliage/prop material | Lit | PBRMaterial |
| Ashen Iron | Metal instance | Lit metallic | PBRMaterial |
| Aether Crystal | Translucent/emissive instance | HDRP/URP emission | PBR + emission |
| Corrupted Stone | Hero corruption instance | Lit + emission | PBR + emission |
| Moss/Lichen | Foliage detail | Lit | PBRMaterial |
| Whisper Lake | Water material | Water shader | WaterMaterial/PBR custom |

## QA gates

- No visible procedural tiling at gameplay camera distance.
- No high-frequency noise that destroys silhouette readability.
- Wet surfaces become darker/glossier without becoming mirror-like.
- Magic materials remain readable through fog without washing out the scene.
- Decals do not overpower traversal markers or combat telegraphs.
- Material variants remain visually coherent across the complete W04 biome.

## Source files

- `data/materials/W04_ASHEN_FOREST_MATERIAL_LIBRARY_v1.json`
- `tools/blender/NARIS_W04_MATERIAL_FACTORY_v1.py`
