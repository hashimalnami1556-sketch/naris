# NARIS Asset Naming Standard

## Canonical ID

`NARIS-W<world>-<domain>-<type>-<sequence>`

Example: `NARIS-W06-ENV-GEO-0001`

## File naming

`<AssetID>_<Descriptor>_<Variant>_<LOD-or-Resolution>_<Version>`

Example:

`NARIS-W06-ENV-GEO-0001_InvertedTower_A_LOD0_V001`

## Environment types

- `GEO` geometry
- `TILE` modular tile
- `CLIFF` cliff kit
- `PROP` environment prop
- `RUIN` ruin/architecture
- `LAND` landmark
- `MAT` material
- `VFX` effect
- `LIGHT` lighting setup
- `AUDIO` environmental audio
- `ARENA` gameplay/boss arena

## World IDs

- W01 Frozen Peaks
- W02 Forge of Flame
- W03 Echoes Desert
- W04 Ashen Forest
- W05 Silent Abyss
- W06 Inverted Towers
- W07 Lost Souls Swamp
- W08 Astral Fortress
- W09 Forgotten Canals
- W10 Throne of Naris

## Rules

- IDs are immutable after assignment.
- Variants use `_A`, `_B`, `_C` rather than descriptive ad-hoc suffixes.
- LOD values use `LOD0`, `LOD1`, `LOD2`, `LOD3`.
- Versions use `V001`, `V002`, etc.
- Source files and exported runtime files retain the same canonical Asset ID.
- Do not use spaces or ambiguous abbreviations.
