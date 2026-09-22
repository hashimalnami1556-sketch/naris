# NARIS v1.9 — Master Integration Specification

**Date:** 2026-09-22  
**Canonical target:** Unreal Engine 5.4+ / Windows PC  
**Slice:** W04 — Ashen Forest

## Purpose

The project previously accumulated strong systems in layered prototype packages. v1.9 defines the merge point: one production repository, one asset registry, one W04 gameplay loop and one Unreal-first implementation path.

The goal is **not** to preserve every prototype implementation. The goal is to preserve validated design/runtime contracts and re-home them into the canonical Unreal project.

## Source layers

| Layer | Preserve |
|---|---|
| v1.3 | branding, visual language, color bible |
| v1.4 | combat/energy/ability contracts |
| v1.5 | quest, inventory, dialogue, interaction contracts |
| v1.6 | companion, crafting, map, AI/faction/event contracts |
| v1.7 | boss, cinematic, localization, settings, build/QA contracts |
| v1.8 | GameRoot/demo flow, saves, achievements, release gates |
| v1.9 | merge policy, platform packaging, playtest, validation |

## Canonical implementation rule

- Unreal implementation beats legacy prototype code when both exist.
- `data/MASTER_ASSET_REGISTRY.json` is authoritative for production asset identity/status.
- `NARIS_MASTER/` contains the master production workspace.
- `DOCUMENTS/` is provenance/archive, not a second source of truth.
- generated images are references until passed through the asset pipeline.
- Windows PC is the first executable acceptance target.
- public demo remains blocked until release gates pass.

## W04 runtime graph

    GameInstance
    ├── Save/Profile
    ├── Localization/Settings
    └── W04 GameMode
        ├── Player / Ashen Vessel
        │   ├── Enhanced Input
        │   ├── Combat
        │   ├── Energy/Essence
        │   ├── Inventory
        │   └── Interaction
        ├── Celestial Wolf
        │   ├── Companion Commands
        │   └── Echo Link
        ├── Quest State
        ├── Dialogue State
        ├── Checkpoints
        ├── Encounter Director
        ├── Bone Beast
        │   ├── Phases
        │   ├── Telegraphs
        │   └── Rewards
        └── UMG HUD
            ├── HP
            ├── Energy
            ├── Resonance
            ├── Boss Bar
            └── Quest/Interaction Feedback

## Demo flow

`MainMenu → IntroCinematic → WakeArea → CombatTutorial → MemoryCrystal → FirstWhisper → AshGate → CelestialWolf → BoneBeastArena → DemoEnd`

## World-generation bridge

AssetForge creates deterministic source data only.

    AssetForge JSON
    ├── heightmap
    ├── biome grid / 99-biome catalog
    ├── rivers
    ├── settlements
    ├── roads
    └── chunks
            ↓
    Unreal Import Bridge
    ├── Landscape/height source
    ├── PCG biome masks
    ├── Water/Spline guides
    ├── settlement POI markers
    ├── road splines
    └── World Partition metadata

Authored level design remains authoritative for combat spaces, quest beats, traversal, landmarks and cinematics.

## PC acceptance target

Minimum internal package:

- Windows x64
- keyboard/mouse
- Xbox-style controller
- 1080p baseline
- scalable quality settings
- save slot + autosave
- EN/AR localization
- crash-free 10–15 minute slice
- performance capture and QA report

## Blocking gates

The slice cannot be promoted to public demo while any of these are true:

- player cannot finish the loop
- boss encounter blocks progression
- save state corrupts or loses mandatory progression
- unhandled crash exists in normal play
- input/controller path is incomplete
- packaging is not reproducible
- major UI/localization overflow blocks interaction
- unlicensed/untracked production assets are included

## Validation

Fast world-generator test:

    cd tools/assetforge
    python -m unittest test_world_generator.py

Expected: four passing tests covering 99-biome catalog, determinism, chunk shape and JSON export.
