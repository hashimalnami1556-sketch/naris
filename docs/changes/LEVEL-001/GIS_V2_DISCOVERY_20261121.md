# LEVEL-001 — Local Jeddah GIS V2 discovery and Unreal 5.7 validation

Date: 2026-11-21. This record corrects the earlier assumption that the prior Jeddah design was not accessible. An actual previously authored local GIS stage and its source data were inspected on the authorized AsusRog workstation. The remote map binaries and data are **NOT part of this GitHub PR**.

## Authoritative local inventory
- Project: `C:\Users\Admin\NARIS\NARIS.uproject` — UE EngineAssociation 5.7; `UnrealEditor.exe` installed in `C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64`.
- Local project’s **already existing** approved GIS map: `Content\NARIS_GIS\Jeddah\Maps\L_Jeddah_GIS_V2.umap`, 10,414,445 bytes, last modified 2026-10-02.
- Explicit prior decision: `07_Docs\Worlds\NARIS_JEDDAH_WORLD_ADOPTION.md` dated 2026-10-02 identifies `L_Jeddah_RedSea_V1` as NOT Jeddah; excludes it from world selection and MapsToCook. GIS V2 remains intentionally excluded from Shipping until visual, navigation and performance review.
- Raw true location-derived OSM cache: `Saved\GIS\Jeddah\osm_jeddah_core.json` (16,281,464 bytes); derived `jeddah_gis_v2.json` (4,590,335 bytes).
- OSM bbox lat 21.45–21.58 N / lon 39.12–39.25 E; origin 21.5150 N / 39.1850 E. Source attribution: © OpenStreetMap contributors, ODbL 1.0.
- Cache counts reported in local adoption note: 8,046 road ways, 13,302 buildings.
- Local `jeddah_unreal_v2_report.json` reports `roads_spawned=952`, `road_segments=2800`, `buildings_spawned=2200`, `actor_count=5004`, `saved=true`, `asset_exists=true`, `passed=true`. Do not confuse all road ways with instanced segments, or all OSM buildings with instanced actor count.

## Actual content limitations (direct source inspection)
`Pipeline/Unreal/author_jeddah_gis_v2.py` creates each building as `/Engine/BasicShapes/Cube` scaled to its **axis-aligned bounding box**; each road segment is a scaled cube oriented by heading. The footprints and rough heights exist in the JSON source, but are not yet represented as detailed extruded per-building silhouettes and facades. GPS/OSM alignment alone does not prove photographic realism or road usability. Some heights are estimated from OSM levels or defaults. This is a real-geography-driven **blockout**, not a photoreal digital twin.

## Checks run on AsusRog
- `py -3 -m unittest discover -s Pipeline\GIS\tests -p test*.py -v`: 4 passed (real workstation).
- UE Editor binary verified as installed, editor log identified actual UE **5.7.4**.
- Launched editor from actual NARIS.uproject with existing `Pipeline/Unreal/capture_jeddah_gis_v2.py`.
- UE log shows `MAP LOAD ...L_Jeddah_GIS_V2.umap`, loaded world, and `MapCheck: ...0 Error(s), 0 Warning(s)`.
- Original async screenshot attempt exited without `Jeddah_GIS_V2_Review.png` being written. Subsequently authored `Saved\GIS\Jeddah\LEVEL001_baseline_capture.py` under Saved only; no tracked source or .umap was modified. See execution status separately; a missing screenshot must not be claimed as captured.
- Runtime gameplay network, Cook, Windows package, FPS, memory, texture fit, Lumen and NavMesh: **NOT RUN**.

## Safety and source protection
- Local git branch `feature/local-ui5-4-bell-marsh-20261003`, HEAD `57676f5`, working tree already dirty with many gameplay maps, C++ and config changes. No checkout, reset, stage, commit or .umap overwrite attempted. Local screenshot script is under `Saved\`, not source control.
- Older self-generated Jeddah RealismPass02 review geometry is procedurally fictional in street layout, **must not replace authoritative GIS V2**. It may contribute separately licensed modular assets if and only if source provenance and measurements are validated.
- Do not change world routing/shipping inclusion until automated and visual validation succeeds.

## Correct next engineering change (separate gated ID)
1. Baseline with deterministic seed/camera/resolution and saved screenshot, map validation, and local git state; fix capture automation first if required.
2. Produce an **isolated GIS V3 review map** from full true OSM polygon footprints, preserving OSM ids, scale and coordinates; never modify `L_Jeddah_GIS_V2.umap` in place.
3. Upgrade certified facade/rawasheen, PBR materials and night lighting in a bounded focal district, retain existing road geometry constraints.
4. Generate before/after/diff with exact identical camera settings; manually verify navigability, spawn, collisions, Q/A and provenance.
5. Run Build Development, Cook, Project.* tests, server+2 clients, fpschart, shipping separation checks, and Rollback. Only after those gates consider making GIS V3 user-selectable.

**Status: EXISTING_GIS_V2_LOADED_IN_EDITOR; photorealism/Shipping RUNTIME NOT VERIFIED.**
