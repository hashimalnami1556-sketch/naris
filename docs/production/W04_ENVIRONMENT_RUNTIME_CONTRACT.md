# W04 Ashen Forest — Environment Runtime Contract

Updated: 2026-09-23

This document defines source precedence for the W04 environment pipeline. It does **not** rewrite or erase older design/reference files; it prevents their differing values from being mixed into runtime generation.

## Authoritative sources by concern

| Concern | Runtime authority | Notes |
|---|---|---|
| Macro zone layout / critical path | `NARIS_MASTER/09_WORLD/Ashen_Forest/LEVEL_LAYOUT.json` | Six zones Z01-Z06 and macro bounds. |
| Runtime environment generator dimensions | `data/environments/W04_AshenForest_environment_factory_v2.json` | Schema 2.1.0; used directly by Blender Factory v2. |
| Lighting intent | `NARIS_MASTER/09_WORLD/Ashen_Forest/LIGHTING_PLAN.json` | Permanent late-dusk, warm key, cool mist fill, readability-first rule. |
| Hero environment asset budgets | `data/environments/W04_ASHEN_FOREST_WAVE2_ASSET_CATALOG.json` | Used for documented per-asset budgets such as Ash Gate 22k LOD0 triangles. |
| Expanded location concepts | `data/environments/W04_ASHEN_FOREST_WAVE3_HERO_LOCATIONS.json` | Design/reference expansion; not runtime streaming configuration. |
| Legacy modular kit reference | `data/environments/W04_AshenForest_modular_kit.json` | Earlier kit/performance reference; not runtime streaming authority. |

## Canonical runtime values

Derived from `W04_AshenForest_environment_factory_v2.json`:

- Snap grid: **1.0 m**
- Floor module: **4.0 m**
- Wall module: **4.0 m**
- Standard height: **3.5 m**
- Door width: **2.0 m**
- Stair step: **0.25 m**
- Streaming cell: **128 m**
- Preload radius: **256 m**
- LOD hysteresis: **32 m**
- Material slots max per environment mesh: **4**
- Texture ceiling: **4K**
- Zone draw-call budget: **1800**
- Shadow distance target: **80 m**

These are configuration targets, not proof that a shipped map meets performance.

## Known source divergences

### Grid

- Factory v2: `grid_m = 1.0`
- Modular Kit v1: `grid_m = 1.0`
- Wave2 catalog: `grid = 2.0`

**Runtime decision:** 1 m is the snap grid. Wave2's 2 m value remains a Wave2 catalog/grid convention and must not overwrite Factory v2.

### Streaming cell

- Factory v2: **128 m**
- Wave2 catalog: **32 m**
- Wave3 hero locations: **32 m**

**Runtime decision:** Factory v2's 128 m value is the current generation/runtime configuration. The 32 m values remain design/reference values until measured Windows profiling justifies changing the runtime contract.

### LOD distance policy

- Legacy modular kit: **25 / 60 / 120 m**
- Previous Blender factory metadata: **32 / 80 / 160 m**
- Factory v2 contract: semantic tiers `LOD0 hero / LOD1 gameplay / LOD2 distance / LOD3 impostor_or_hidden`

**Runtime decision:** the old hard-coded `32/80/160m` metadata was removed. Factory v2 records semantic LOD policy. Exact screen-size/distance thresholds require measured engine profiling and are not treated as final by source-only validation.

## Map separation

- Development runtime smoke: `/Game/NARIS/W04/Maps/W04_Prototype`
- Production assembly blockout: `/Game/NARIS/W04/Maps/W04_AshenForest_Blockout`
- Shipping production map: `/Game/NARIS/W04/Maps/W04_AshenForest`

Shipping RC rejects `DEV_*`, `BLOCKOUT_*`, and `NARIS_RuntimeSmokeDirector`, and requires the six canonical zone markers plus navigation/lighting actors.

## Current Blender rule

`tools/blender/NARIS_W04_ASHEN_FOREST_FACTORY_v2.py` reads Factory v2 JSON directly. It must not maintain independent copies of grid, module, streaming, collision, or LOD policy values.

The factory may produce source/exchange evidence, but Blender generation/export success is not Unreal gameplay or Shipping evidence.
