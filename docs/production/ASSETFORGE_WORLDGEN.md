# AssetForge — World Generation Layer

## Scope

`tools/assetforge/world_generator.py` is a deterministic, standard-library-only source-data generator for CALL OF NARIS.

It is designed to feed Unreal tooling, not replace authored level design.

## Current capabilities

- deterministic seed-based generation
- normalized heightmap
- moisture and temperature fields
- 99-biome catalog (11 families × 9 variants)
- biome assignment
- downhill river guide paths
- settlement placement on buildable terrain
- minimum-spanning road guides
- chunk metadata for streaming/World Partition planning
- JSON export

## Default profile

See `data/worldgen/worldgen_profile_v1.json`.

Default target:

- map: 256 × 256 source cells
- chunks: 32 × 32
- settlements: 12
- rivers: 8
- sea level: 0.33
- seed: 9042026

## Run

    python tools/assetforge/world_generator.py --size 256 --chunk-size 32 --output build/worldgen/naris_world.json

## Test

    cd tools/assetforge
    python -m unittest test_world_generator.py

## Unreal bridge contract

| Output | Unreal use |
|---|---|
| `heightmap` | Landscape import/transcode source |
| `biomes` | PCG/landscape material mask source |
| `rivers` | Water/Spline guide |
| `settlements` | POI / encounter / settlement seed markers |
| `roads` | Spline guide |
| `chunks` | World Partition planning metadata |

## Production constraint

Procedural generation is a **layout accelerator**. W04 narrative landmarks, boss arenas, traversal gates, cinematics, quests and authored combat spaces remain hand-controlled.

## Next implementation

1. Add PNG/R16 heightmap exporter.
2. Add biome-mask image exporter.
3. Add Unreal Editor Python import bridge.
4. Map biome IDs to `data/environments/NARIS_ENVIRONMENT_BIOME_MATRIX_v1.json`.
5. Add erosion pass and river accumulation.
6. Add settlement archetype tables.
7. Add landmark exclusion/placement masks.
8. Add deterministic regression snapshots.
